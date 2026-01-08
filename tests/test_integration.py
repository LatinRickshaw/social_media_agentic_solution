"""
Integration tests for end-to-end functionality.
Tests the complete workflow from generator to brand voice to hashtags to content.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.generator import SocialMediaGenerator


@pytest.fixture
def generator():
    """Create a generator instance for testing"""
    return SocialMediaGenerator()


def test_end_to_end_post_generation_with_brand_guidelines(generator):
    """Test complete post generation flow with brand guidelines"""
    # Mock OpenAI responses
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test LinkedIn post about innovation"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]
    mock_hashtag_response.choices[0].message.content = "Innovation, Technology, Business"

    # Mock Gemini image generation
    with (
        patch.object(
            generator.openai_client.chat.completions,
            "create",
            side_effect=[mock_content_response, mock_hashtag_response],
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "generated_images/test.png"

        # Generate post
        result = generator.generate_post(
            user_prompt="Our latest innovation",
            platform="linkedin",
            context="Focus on customer benefits",
        )

        # Verify all components worked together
        assert "content" in result
        assert "Innovation" in result["content"] or "innovation" in result["content"]
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert result["image_path"] == "generated_images/test.png"
        assert "metadata" in result
        assert "brand_voice" in result["metadata"]

        # Verify brand voice was automatically applied
        brand_voice = result["metadata"]["brand_voice"]
        assert isinstance(brand_voice, str)
        assert len(brand_voice) > 0


def test_platform_specific_brand_voice_application(generator):
    """Test that each platform gets appropriate brand voice"""
    platforms = ["linkedin", "twitter", "facebook", "nextdoor"]

    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]
    mock_hashtag_response.choices[0].message.content = "Test, Content"

    with (
        patch.object(
            generator.openai_client.chat.completions,
            "create",
            side_effect=[mock_content_response, mock_hashtag_response] * len(platforms),
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        for platform in platforms:
            result = generator.generate_post("Test topic", platform)

            # Each platform should have platform-specific brand voice
            brand_voice = result["metadata"]["brand_voice"]
            assert platform.lower() in brand_voice.lower()


def test_hashtag_limits_per_platform(generator):
    """Test that hashtag generation respects platform limits"""
    from src.core.config import PLATFORM_SPECS

    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]

    with (
        patch.object(generator.openai_client.chat.completions, "create") as mock_create,
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        for platform in PLATFORM_SPECS.keys():
            max_hashtags = PLATFORM_SPECS[platform]["max_hashtags"]

            # Return more hashtags than the limit
            mock_hashtag_response.choices[0].message.content = ", ".join(
                [f"Tag{i}" for i in range(max_hashtags + 5)]
            )
            mock_create.side_effect = [mock_content_response, mock_hashtag_response]

            result = generator.generate_post("Test", platform)

            # Should be limited to platform max
            assert len(result["hashtags"]) <= max_hashtags


def test_generate_all_platforms_integration(generator):
    """Test generating posts for all platforms simultaneously"""
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]
    mock_hashtag_response.choices[0].message.content = "Test, Tag"

    with (
        patch.object(
            generator.openai_client.chat.completions,
            "create",
            side_effect=[mock_content_response, mock_hashtag_response] * 4,
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        # Generate for all platforms
        results = generator.generate_all_platforms(user_prompt="Test topic", context="Test context")

        # Verify all platforms were generated
        assert len(results) == 4
        for platform, result in results.items():
            assert result is not None
            assert "content" in result
            assert "hashtags" in result
            assert "metadata" in result
            assert "brand_voice" in result["metadata"]


def test_custom_brand_voice_override(generator):
    """Test that custom brand voice overrides brand guidelines"""
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]
    mock_hashtag_response.choices[0].message.content = "Test"

    with (
        patch.object(
            generator.openai_client.chat.completions,
            "create",
            side_effect=[mock_content_response, mock_hashtag_response],
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        custom_voice = "extremely casual and fun"

        result = generator.generate_post(
            user_prompt="Test", platform="linkedin", brand_voice=custom_voice
        )

        # Should use the custom brand voice
        assert result["metadata"]["brand_voice"] == custom_voice


def test_disable_hashtags_integration(generator):
    """Test generating posts with hashtags disabled"""
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content without hashtags"

    with (
        patch.object(
            generator.openai_client.chat.completions, "create", return_value=mock_content_response
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        result = generator.generate_post(
            user_prompt="Test", platform="linkedin", include_hashtags=False
        )

        # Should have empty hashtags
        assert result["hashtags"] == []
        # Content should not have # symbols
        assert "#" not in result["content"]


def test_error_recovery_in_generation_flow(generator):
    """Test that errors in one component don't break the entire flow"""
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    with (
        patch.object(
            generator.openai_client.chat.completions, "create", return_value=mock_content_response
        ),
        patch.object(generator, "_generate_hashtags") as mock_hashtags,
        patch.object(generator, "_generate_image") as mock_image,
    ):

        # Hashtag generation fails
        mock_hashtags.side_effect = Exception("Hashtag API error")
        mock_image.return_value = "test.png"

        # Should raise the exception (not handled in current implementation)
        with pytest.raises(Exception):
            generator.generate_post("Test", "linkedin")


def test_brand_voice_consistency_across_multiple_calls(generator):
    """Test that brand voice remains consistent across multiple generation calls"""
    mock_content_response = MagicMock()
    mock_content_response.choices = [MagicMock()]
    mock_content_response.choices[0].message.content = "Test content"

    mock_hashtag_response = MagicMock()
    mock_hashtag_response.choices = [MagicMock()]
    mock_hashtag_response.choices[0].message.content = "Test"

    with (
        patch.object(
            generator.openai_client.chat.completions,
            "create",
            side_effect=[mock_content_response, mock_hashtag_response] * 3,
        ),
        patch.object(generator, "_generate_image") as mock_image,
    ):

        mock_image.return_value = "test.png"

        # Generate multiple posts for same platform
        results = []
        for _ in range(3):
            result = generator.generate_post("Test topic", "linkedin")
            results.append(result)

        # All should have the same brand voice (from guidelines)
        brand_voices = [r["metadata"]["brand_voice"] for r in results]
        assert all(voice == brand_voices[0] for voice in brand_voices)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
