"""
Test script for platform-specific templates and optimization.
Tests templates with various sample prompts to evaluate quality and appropriateness.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.prompt_templates import PLATFORM_TEMPLATES  # noqa: E402


def test_template_structure():
    """Test that all required templates exist and have proper structure"""
    required_platforms = ["linkedin", "twitter", "facebook", "nextdoor"]

    print("=" * 70)
    print("  TEMPLATE STRUCTURE TEST")
    print("=" * 70)

    for platform in required_platforms:
        if platform in PLATFORM_TEMPLATES:
            print(f"✓ {platform}: Template exists")

            # Check for required template variables
            template = PLATFORM_TEMPLATES[platform]
            required_vars = ["{topic}", "{context}", "{brand_voice}"]

            for var in required_vars:
                if var in template:
                    print(f"  ✓ Contains {var}")
                else:
                    print(f"  ✗ Missing {var}")
        else:
            print(f"✗ {platform}: Template missing!")

    print()


def test_sample_prompts():
    """Test templates with sample prompts"""

    sample_prompts = [
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

    print("=" * 70)
    print("  SAMPLE PROMPT TEST")
    print("=" * 70)

    for idx, prompt in enumerate(sample_prompts, 1):
        print(f"\n--- Sample Prompt {idx} ---")
        print(f"Topic: {prompt['topic']}")
        print(f"Context: {prompt['context']}")
        print(f"Brand Voice: {prompt['brand_voice']}")
        print()

        for platform, template in PLATFORM_TEMPLATES.items():
            formatted = template.format(**prompt)
            print(f"▸ {platform.upper()}:")
            print(f"  Template length: {len(formatted)} characters")

            # Check if template provides clear guidance
            guidance_keywords = ["Requirements:", "Format:", "tone", "hashtag"]
            found = [kw for kw in guidance_keywords if kw.lower() in formatted.lower()]
            print(f"  Guidance elements: {', '.join(found)}")
            print()


def analyze_platform_differentiation():
    """Analyze how templates differ per platform"""

    print("=" * 70)
    print("  PLATFORM DIFFERENTIATION ANALYSIS")
    print("=" * 70)

    platforms = ["linkedin", "twitter", "facebook", "nextdoor"]

    for platform in platforms:
        template = PLATFORM_TEMPLATES[platform]

        print(f"\n{platform.upper()}:")
        print("-" * 40)

        # Extract tone guidance
        if "tone" in template.lower():
            lines = [line for line in template.split("\n") if "tone" in line.lower()]
            for line in lines:
                print(f"  Tone: {line.strip()}")

        # Extract length guidance
        if "word" in template.lower() or "character" in template.lower():
            lines = [
                line
                for line in template.split("\n")
                if "word" in line.lower() or "character" in line.lower()
            ]
            for line in lines:
                print(f"  Length: {line.strip()}")

        # Extract hashtag guidance
        if "hashtag" in template.lower():
            lines = [line for line in template.split("\n") if "hashtag" in line.lower()]
            for line in lines:
                print(f"  Hashtags: {line.strip()}")


def check_brand_voice_integration():
    """Check if templates properly integrate brand voice parameter"""

    print("\n" + "=" * 70)
    print("  BRAND VOICE INTEGRATION CHECK")
    print("=" * 70)

    for platform, template in PLATFORM_TEMPLATES.items():
        has_brand_voice = "{brand_voice}" in template
        references_voice = "voice" in template.lower() or "tone" in template.lower()

        print(f"\n{platform.upper()}:")
        print(f"  Has brand_voice parameter: {'✓' if has_brand_voice else '✗'}")
        print(f"  References voice/tone: {'✓' if references_voice else '✗'}")

        if has_brand_voice:
            # Show context around brand_voice usage
            lines = template.split("\n")
            for i, line in enumerate(lines):
                if "{brand_voice}" in line:
                    print(f"  Usage: {line.strip()}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PLATFORM TEMPLATE TESTING SUITE")
    print("=" * 70 + "\n")

    test_template_structure()
    test_sample_prompts()
    analyze_platform_differentiation()
    check_brand_voice_integration()

    print("\n" + "=" * 70)
    print("  TEST SUITE COMPLETE")
    print("=" * 70 + "\n")
