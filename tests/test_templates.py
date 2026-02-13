"""
Tests for platform-specific templates and optimization.
Validates templates have proper structure, accept sample prompts,
differentiate per platform, and integrate brand voice.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.prompt_templates import PLATFORM_TEMPLATES  # noqa: E402

REQUIRED_PLATFORMS = ["linkedin", "twitter", "facebook", "nextdoor"]


class TestTemplateStructure:
    """Test that all required templates exist and have proper structure."""

    def test_all_platforms_have_templates(self):
        for platform in REQUIRED_PLATFORMS:
            assert platform in PLATFORM_TEMPLATES, f"Template missing for {platform}"

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_template_contains_required_variables(self, platform):
        template = PLATFORM_TEMPLATES[platform]
        for var in ["{topic}", "{context}", "{brand_voice}"]:
            assert var in template, f"{platform} template missing variable {var}"


class TestSamplePrompts:
    """Test templates render correctly with sample data."""

    SAMPLE_PROMPTS = [
        {
            "topic": "Announcing our new AI-powered feature",
            "context": "Focus on productivity and collaboration benefits",
            "brand_voice": "professional and innovative",
        },
        {
            "topic": "Customer success story spotlight",
            "context": "Highlight 50% efficiency improvement",
            "brand_voice": "friendly and authentic",
        },
        {
            "topic": "Industry trend: Remote work evolution",
            "context": "Thought leadership perspective",
            "brand_voice": "insightful and professional",
        },
    ]

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_templates_format_without_error(self, platform):
        template = PLATFORM_TEMPLATES[platform]
        for prompt in self.SAMPLE_PROMPTS:
            formatted = template.format(**prompt)
            assert len(formatted) > 0

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_formatted_templates_contain_guidance(self, platform):
        template = PLATFORM_TEMPLATES[platform]
        formatted = template.format(**self.SAMPLE_PROMPTS[0])
        guidance_keywords = ["requirements", "format", "tone", "hashtag"]
        found = [kw for kw in guidance_keywords if kw in formatted.lower()]
        assert len(found) > 0, f"{platform} template lacks guidance keywords"


class TestPlatformDifferentiation:
    """Test that templates are meaningfully different across platforms."""

    def test_templates_are_unique(self):
        templates = [PLATFORM_TEMPLATES[p] for p in REQUIRED_PLATFORMS]
        assert len(set(templates)) == len(templates), "Some platform templates are identical"

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_template_references_tone(self, platform):
        template = PLATFORM_TEMPLATES[platform].lower()
        assert (
            "tone" in template or "voice" in template
        ), f"{platform} template should reference tone or voice"


class TestBrandVoiceIntegration:
    """Check that templates properly integrate the brand_voice parameter."""

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_brand_voice_parameter_present(self, platform):
        assert "{brand_voice}" in PLATFORM_TEMPLATES[platform]

    @pytest.mark.parametrize("platform", REQUIRED_PLATFORMS)
    def test_brand_voice_value_appears_in_output(self, platform):
        voice = "uniqueTestVoiceMarker"
        formatted = PLATFORM_TEMPLATES[platform].format(
            topic="test", context="test", brand_voice=voice
        )
        assert voice in formatted
