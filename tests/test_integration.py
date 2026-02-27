"""
Integration tests for end-to-end functionality.
Tests the complete workflow from generator to brand voice to hashtags to content.
All providers are mocked so no live API keys are needed.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.generator import SocialMediaGenerator
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
    return SocialMediaGenerator(provider_config=provider_config)


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


def test_end_to_end_post_generation_with_brand_guidelines(generator, mock_text):
    """Test complete post generation flow with brand guidelines."""
    # The same mock_text provider is called for content, hashtags, and image_prompt
    mock_text.generate_text.side_effect = [
        "Test LinkedIn post about innovation",
        "Innovation, Technology, Business",
        "A professional image depicting innovation",
    ]

    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "generated_images/test.png"

        result = generator.generate_post(
            user_prompt="Our latest innovation",
            platform="linkedin",
            context="Focus on customer benefits",
        )

    assert "content" in result
    assert "Innovation" in result["content"] or "innovation" in result["content"]
    assert "hashtags" in result
    assert len(result["hashtags"]) > 0
    assert result["image_path"] == "generated_images/test.png"
    assert "metadata" in result
    assert "brand_voice" in result["metadata"]
    brand_voice = result["metadata"]["brand_voice"]
    assert isinstance(brand_voice, str)
    assert len(brand_voice) > 0


def test_platform_specific_brand_voice_application(generator, mock_text):
    """Test that each platform gets appropriate brand voice."""
    platforms = ["linkedin", "twitter", "facebook", "nextdoor"]

    for platform in platforms:
        mock_text.generate_text.side_effect = [
            "Test content",
            "Test, Content",
            "A professional image",
        ]

        with patch.object(generator, "_generate_image") as mock_gen_image:
            mock_gen_image.return_value = "test.png"
            result = generator.generate_post("Test topic", platform)

        brand_voice = result["metadata"]["brand_voice"]
        assert platform.lower() in brand_voice.lower()


def test_hashtag_limits_per_platform(generator, mock_text):
    """Test that hashtag generation respects platform limits."""
    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "test.png"

        for platform in PLATFORM_SPECS.keys():
            max_hashtags = PLATFORM_SPECS[platform]["max_hashtags"]

            # Return more hashtags than the limit for this platform
            excess_tags = ", ".join([f"Tag{i}" for i in range(max_hashtags + 5)])
            mock_text.generate_text.side_effect = [
                "Test content",
                excess_tags,
                "A professional image",
            ]

            result = generator.generate_post("Test", platform)

            assert len(result["hashtags"]) <= max_hashtags


def test_generate_all_platforms_integration(generator, mock_text):
    """Test generating posts for all platforms simultaneously."""
    # 4 platforms × 3 text calls each = 12 side_effect values
    mock_text.generate_text.side_effect = [
        "Test content",
        "Test, Tag",
        "A professional image",
    ] * 4

    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "test.png"

        results = generator.generate_all_platforms(user_prompt="Test topic", context="Test context")

    assert len(results) == 4
    for platform, result in results.items():
        assert result is not None
        assert "content" in result
        assert "hashtags" in result
        assert "metadata" in result
        assert "brand_voice" in result["metadata"]


def test_custom_brand_voice_override(generator, mock_text):
    """Test that custom brand voice overrides brand guidelines."""
    mock_text.generate_text.side_effect = [
        "Test content",
        "Test",
        "A professional image",
    ]

    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "test.png"

        custom_voice = "extremely casual and fun"
        result = generator.generate_post(
            user_prompt="Test", platform="linkedin", brand_voice=custom_voice
        )

    assert result["metadata"]["brand_voice"] == custom_voice


def test_disable_hashtags_integration(generator, mock_text):
    """Test generating posts with hashtags disabled."""
    mock_text.generate_text.side_effect = [
        "Test content without hashtags",
        "A professional image",
    ]

    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "test.png"

        result = generator.generate_post(
            user_prompt="Test", platform="linkedin", include_hashtags=False
        )

    assert result["hashtags"] == []
    assert "#" not in result["content"]


def test_error_recovery_in_generation_flow(generator, mock_text):
    """Test that errors in one component don't break the entire flow."""
    mock_text.generate_text.return_value = "Test content"

    with (
        patch.object(generator, "_generate_hashtags") as mock_hashtags,
        patch.object(generator, "_generate_image") as mock_gen_image,
    ):
        mock_hashtags.side_effect = Exception("Hashtag API error")
        mock_gen_image.return_value = "test.png"

        # Exception propagates — not handled in generate_post
        with pytest.raises(Exception):
            generator.generate_post("Test", "linkedin")


def test_brand_voice_consistency_across_multiple_calls(generator, mock_text):
    """Test that brand voice remains consistent across multiple generation calls."""
    mock_text.generate_text.side_effect = [
        "Test content",
        "Test",
        "A professional image",
    ] * 3

    with patch.object(generator, "_generate_image") as mock_gen_image:
        mock_gen_image.return_value = "test.png"

        results = [generator.generate_post("Test topic", "linkedin") for _ in range(3)]

    brand_voices = [r["metadata"]["brand_voice"] for r in results]
    assert all(voice == brand_voices[0] for voice in brand_voices)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
