"""
Unit tests for the social media generator.
"""

import pytest
from unittest.mock import patch
from src.core.generator import SocialMediaGenerator
from src.core.config import PLATFORM_SPECS


@pytest.fixture
def generator():
    """Create a generator instance for testing"""
    with patch("src.core.generator.ChatOpenAI"), patch("src.core.generator.genai"):
        return SocialMediaGenerator()


def test_generator_initialization(generator):
    """Test that generator initializes correctly"""
    assert generator is not None
    assert generator.platform_specs == PLATFORM_SPECS
    assert generator.templates is not None


def test_generate_post_linkedin(generator):
    """Test generating a LinkedIn post"""
    # Mock the LLM chain
    with patch.object(generator, "_generate_content") as mock_content, patch.object(
        generator, "_create_image_prompt"
    ) as mock_image_prompt, patch.object(generator, "_generate_image") as mock_image:

        mock_content.return_value = "Test LinkedIn post content"
        mock_image_prompt.return_value = "Test image prompt"
        mock_image.return_value = "test_image.jpg"

        result = generator.generate_post("Test topic", "linkedin", "Test context", "professional")

        assert result["content"] == "Test LinkedIn post content"
        assert result["image_path"] == "test_image.jpg"
        assert result["platform"] == "linkedin"
        assert "metadata" in result


def test_generate_post_twitter(generator):
    """Test generating a Twitter post"""
    with patch.object(generator, "_generate_content") as mock_content, patch.object(
        generator, "_create_image_prompt"
    ) as mock_image_prompt, patch.object(generator, "_generate_image") as mock_image:

        # Test with content under 280 chars
        mock_content.return_value = "Short tweet"
        mock_image_prompt.return_value = "Test image prompt"
        mock_image.return_value = "test_image.jpg"

        result = generator.generate_post("Test topic", "twitter", "", "casual")

        assert len(result["content"]) <= 280
        assert result["platform"] == "twitter"


def test_generate_all_platforms(generator):
    """Test generating posts for all platforms"""
    with patch.object(generator, "generate_post") as mock_generate:
        mock_generate.return_value = {
            "content": "Test content",
            "image_path": "test.jpg",
            "platform": "test",
        }

        result = generator.generate_all_platforms("Test topic")

        assert len(result) == 4  # All platforms
        assert "linkedin" in result
        assert "twitter" in result
        assert "facebook" in result
        assert "nextdoor" in result


def test_invalid_platform(generator):
    """Test that invalid platform raises error"""
    with pytest.raises(ValueError):
        generator.generate_post("Test", "invalid_platform")


def test_character_limit_validation(generator):
    """Test that character limits are enforced"""
    with patch.object(generator.content_generator, "predict") as mock_predict:
        # Simulate content over Twitter limit
        long_content = "x" * 300
        mock_predict.return_value = long_content

        # Twitter has 280 char limit
        content = generator._generate_content("Test", "twitter", "", "")

        # Should be truncated
        assert len(content) <= 280


def test_regenerate_image(generator):
    """Test regenerating an image for existing content"""
    with patch.object(generator, "_create_image_prompt") as mock_prompt, patch.object(
        generator, "_generate_image"
    ) as mock_image:

        mock_prompt.return_value = "New image prompt"
        mock_image.return_value = "new_image.jpg"

        result = generator.regenerate_image("Test content", "linkedin", "Test topic")

        assert result["image_path"] == "new_image.jpg"
        assert result["image_prompt"] == "New image prompt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
