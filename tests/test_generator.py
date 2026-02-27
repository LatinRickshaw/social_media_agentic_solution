"""
Unit tests for the social media generator.

All tests inject a ProviderConfig with MagicMock provider instances so no
live API keys are needed and no SDK clients are instantiated.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.generator import (
    SocialMediaGenerator,
    retry_with_exponential_backoff,
)
from src.core.providers.base import TextProvider, ImageProvider, ProviderConfig
from src.core.config import PLATFORM_SPECS


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_text():
    return MagicMock(spec=TextProvider)


@pytest.fixture
def mock_image():
    return MagicMock(spec=ImageProvider)


@pytest.fixture
def provider_config(mock_text, mock_image):
    return ProviderConfig(
        content=mock_text,
        hashtags=mock_text,
        image_prompt=mock_text,
        image=mock_image,
    )


@pytest.fixture
def generator(provider_config):
    """Create a generator instance with injected mock providers."""
    return SocialMediaGenerator(provider_config=provider_config)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


def test_generator_initialization(provider_config):
    """Test that generator initialises correctly from an injected ProviderConfig."""
    gen = SocialMediaGenerator(provider_config=provider_config)

    assert gen is not None
    assert gen.platform_specs == PLATFORM_SPECS
    assert gen.templates is not None
    assert gen._provider_config is provider_config


def test_generator_uses_config_default_when_no_provider_config_given():
    """When provider_config is omitted, Config.default_provider_config() is used."""
    mock_text = MagicMock(spec=TextProvider)
    mock_image = MagicMock(spec=ImageProvider)
    fake_pc = ProviderConfig(
        content=mock_text, hashtags=mock_text, image_prompt=mock_text, image=mock_image
    )
    with patch("src.core.generator.Config.default_provider_config", return_value=fake_pc):
        gen = SocialMediaGenerator()
    assert gen._provider_config is fake_pc


def test_generator_initialization_missing_api_keys():
    """Test that generator raises when Config.default_provider_config fails."""
    with patch(
        "src.core.generator.Config.default_provider_config",
        side_effect=ValueError("API key missing"),
    ):
        with pytest.raises(ValueError, match="API key missing"):
            SocialMediaGenerator()


# ---------------------------------------------------------------------------
# generate_post / generate_all_platforms
# ---------------------------------------------------------------------------


def test_generate_post_linkedin(generator):
    """Test generating a LinkedIn post."""
    with (
        patch.object(generator, "_generate_content") as mock_content,
        patch.object(generator, "_create_image_prompt") as mock_image_prompt,
        patch.object(generator, "_generate_image") as mock_image,
        patch.object(generator, "_generate_hashtags") as mock_hashtags,
    ):

        mock_content.return_value = "Test LinkedIn post content about productivity"
        mock_image_prompt.return_value = "Professional office environment with collaboration"
        mock_image.return_value = "generated_images/linkedin_123.png"
        mock_hashtags.return_value = ["Productivity", "Business", "Innovation"]

        result = generator.generate_post("Test topic", "linkedin", "Test context", "professional")

        assert "Test LinkedIn post content about productivity" in result["content"]
        assert result["image_path"] == "generated_images/linkedin_123.png"
        assert result["platform"] == "linkedin"
        assert "metadata" in result
        assert result["metadata"]["char_limit"] == 3000
        assert "hashtags" in result
        assert len(result["hashtags"]) == 3


def test_generate_post_twitter(generator):
    """Test generating a Twitter post."""
    with (
        patch.object(generator, "_generate_content") as mock_content,
        patch.object(generator, "_create_image_prompt") as mock_image_prompt,
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_content.return_value = "Short tweet under 280 chars"
        mock_image_prompt.return_value = "Test image prompt"
        mock_image.return_value = "generated_images/twitter_123.png"

        result = generator.generate_post("Test topic", "twitter", "", "casual")

        assert len(result["content"]) <= 280
        assert result["platform"] == "twitter"
        assert result["metadata"]["char_limit"] == 280


def test_generate_all_platforms(generator):
    """Test generating posts for all platforms."""
    with patch.object(generator, "generate_post") as mock_generate:
        mock_generate.return_value = {
            "content": "Test content",
            "image_path": "test.jpg",
            "image_prompt": "Test prompt",
            "platform": "test",
            "metadata": {},
        }

        result = generator.generate_all_platforms("Test topic")

        assert len(result) == 4
        assert "linkedin" in result
        assert "twitter" in result
        assert "facebook" in result
        assert "nextdoor" in result


def test_invalid_platform(generator):
    """Test that invalid platform raises error."""
    with pytest.raises(ValueError, match="Unsupported platform"):
        generator.generate_post("Test", "invalid_platform")


def test_generate_post_without_hashtags(generator):
    """Test generating a post with hashtags disabled."""
    with (
        patch.object(generator, "_generate_content") as mock_content,
        patch.object(generator, "_create_image_prompt") as mock_image_prompt,
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_content.return_value = "Test content"
        mock_image_prompt.return_value = "Test prompt"
        mock_image.return_value = "test.png"

        result = generator.generate_post(
            "Test topic", "linkedin", "", brand_voice="professional", include_hashtags=False
        )

        assert result["hashtags"] == []
        assert "#" not in result["content"]


def test_generate_post_with_brand_guidelines(generator):
    """Test that brand voice from guidelines is used when not specified."""
    with (
        patch.object(generator, "_generate_content") as mock_content,
        patch.object(generator, "_create_image_prompt") as mock_image_prompt,
        patch.object(generator, "_generate_image") as mock_image,
        patch.object(generator, "_generate_hashtags") as mock_hashtags,
    ):

        mock_content.return_value = "Test content"
        mock_image_prompt.return_value = "Test prompt"
        mock_image.return_value = "test.png"
        mock_hashtags.return_value = ["Test"]

        generator.generate_post("Test topic", "linkedin")

        call_args = mock_content.call_args
        brand_voice_arg = call_args[0][3]  # 4th positional argument
        assert brand_voice_arg is not None
        assert isinstance(brand_voice_arg, str)


def test_generate_all_platforms_with_failures(generator):
    """Test that failures in some platforms don't stop others."""
    call_count = 0

    def mock_generate(prompt, platform, context=None, brand_voice=None, include_hashtags=True):
        nonlocal call_count
        call_count += 1
        if platform == "twitter":
            raise Exception("Twitter API failed")
        return {
            "content": f"Content for {platform}",
            "hashtags": [],
            "image_path": "test.jpg",
            "image_prompt": "test",
            "platform": platform,
            "metadata": {},
        }

    with patch.object(generator, "generate_post", side_effect=mock_generate):
        result = generator.generate_all_platforms("Test topic")

        assert call_count == 4
        assert result["twitter"] is None
        assert result["linkedin"] is not None
        assert result["facebook"] is not None
        assert result["nextdoor"] is not None


# ---------------------------------------------------------------------------
# Private generation methods
# ---------------------------------------------------------------------------


def test_character_limit_enforcement(generator, mock_text):
    """Test that content exceeding the char limit triggers regeneration."""
    mock_text.generate_text.return_value = "x" * 300

    with patch.object(generator, "_regenerate_shorter_content") as mock_regen:
        mock_regen.return_value = "Shortened content"
        generator._generate_content("Test", "twitter", "", "professional")
        # Twitter limit is 280; 300-char result should trigger regen
        mock_regen.assert_called_once()


def test_regenerate_shorter_content(generator, mock_text):
    """Test content regeneration for length."""
    mock_text.generate_text.return_value = "This is shorter content"

    result = generator._regenerate_shorter_content(
        "x" * 300, "twitter", 280, "Test topic", "Test context", "professional"
    )

    assert len(result) <= 280


def test_create_image_prompt(generator, mock_text):
    """Test image prompt creation."""
    mock_text.generate_text.return_value = "A professional office scene with people collaborating"

    result = generator._create_image_prompt("Post about teamwork", "linkedin", "Team collaboration")

    assert isinstance(result, str)
    assert len(result) > 0
    mock_text.generate_text.assert_called_once()


def test_hashtag_generation(generator, mock_text):
    """Test hashtag generation."""
    mock_text.generate_text.return_value = "Productivity, Innovation, Business, TechTrends, Growth"

    hashtags = generator._generate_hashtags(
        "Post about productivity tools", "linkedin", "productivity tools"
    )

    assert isinstance(hashtags, list)
    assert len(hashtags) <= 5  # LinkedIn max hashtags
    assert all(isinstance(tag, str) for tag in hashtags)
    mock_text.generate_text.assert_called_once()


def test_platform_specific_hashtag_limits(generator, mock_text):
    """Test that hashtag limits are respected per platform."""
    for platform in PLATFORM_SPECS.keys():
        max_tags = PLATFORM_SPECS[platform]["max_hashtags"]

        mock_text.generate_text.return_value = ", ".join([f"Tag{i}" for i in range(max_tags + 10)])

        hashtags = generator._generate_hashtags("Test content", platform, "test")

        assert len(hashtags) <= max_tags


# ---------------------------------------------------------------------------
# Placeholder image
# ---------------------------------------------------------------------------


def test_create_placeholder_image(generator):
    """Test placeholder image creation."""
    with patch("src.core.generator.Image.new") as mock_image:
        mock_img = MagicMock()
        mock_image.return_value = mock_img

        result = generator._create_placeholder_image("linkedin", "Test prompt")

        assert "linkedin" in result
        assert "placeholder" in result
        assert result.endswith(".png")
        mock_img.save.assert_called_once()


def test_regenerate_image(generator):
    """Test regenerating an image for existing content."""
    with (
        patch.object(generator, "_create_image_prompt") as mock_prompt,
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_prompt.return_value = "New image prompt"
        mock_image.return_value = "generated_images/new_image.jpg"

        result = generator.regenerate_image("Test content", "linkedin", "Test topic")

        assert result["image_path"] == "generated_images/new_image.jpg"
        assert result["image_prompt"] == "New image prompt"


# ---------------------------------------------------------------------------
# Brand voice integration
# ---------------------------------------------------------------------------


def test_brand_voice_integration(generator):
    """Test that brand voice is loaded from guidelines."""
    brand_voice = generator.brand_voice.get_brand_voice("linkedin")

    assert isinstance(brand_voice, str)
    assert len(brand_voice) > 0
    assert any(
        keyword in brand_voice.lower()
        for keyword in ["professional", "innovative", "customer", "transparent", "reliable"]
    )


# ---------------------------------------------------------------------------
# Retry decorator
# ---------------------------------------------------------------------------


def test_retry_decorator_success():
    """Test retry decorator with successful call."""
    mock_func = MagicMock(return_value="success")
    decorated = retry_with_exponential_backoff(max_retries=3)(mock_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_decorator_eventual_success():
    """Test retry decorator with eventual success."""

    def mock_func():
        if mock_func.call_count < 3:
            raise Exception("fail")
        return "success"

    mock_func.call_count = 0

    def counting_func():
        mock_func.call_count += 1
        return mock_func()

    decorated = retry_with_exponential_backoff(max_retries=3, initial_delay=0.01)(counting_func)

    result = decorated()

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_decorator_max_retries():
    """Test retry decorator exceeds max retries."""
    call_count = 0

    def always_fails():
        nonlocal call_count
        call_count += 1
        raise Exception("always fails")

    decorated = retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)(always_fails)

    with pytest.raises(Exception) as exc_info:
        decorated()

    assert "always fails" in str(exc_info.value)
    assert call_count == 3  # Initial + 2 retries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
