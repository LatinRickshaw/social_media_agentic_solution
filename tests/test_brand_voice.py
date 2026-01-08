"""
Unit tests for brand voice utilities.
"""

import pytest
from src.core.brand_voice import BrandVoice


@pytest.fixture
def brand_voice():
    """Create a BrandVoice instance for testing"""
    # Use the default brand guidelines path
    return BrandVoice()


def test_brand_voice_initialization(brand_voice):
    """Test that BrandVoice initializes correctly"""
    assert brand_voice is not None
    assert brand_voice.guidelines is not None
    assert isinstance(brand_voice.guidelines, dict)


def test_brand_voice_loads_guidelines(brand_voice):
    """Test that brand guidelines are loaded properly"""
    guidelines = brand_voice.guidelines

    # Check for expected top-level keys
    assert "brand_voice" in guidelines
    assert "values" in guidelines
    assert "platform_preferences" in guidelines
    assert "hashtag_strategy" in guidelines


def test_get_brand_voice_default(brand_voice):
    """Test getting default brand voice"""
    voice = brand_voice.get_brand_voice()

    assert isinstance(voice, str)
    assert len(voice) > 0
    # Should contain primary brand voice
    assert "professional" in voice.lower() or "friendly" in voice.lower()


def test_get_brand_voice_platform_specific(brand_voice):
    """Test getting platform-specific brand voice"""
    platforms = ["linkedin", "twitter", "facebook", "nextdoor"]

    for platform in platforms:
        voice = brand_voice.get_brand_voice(platform)

        assert isinstance(voice, str)
        assert len(voice) > 0
        # Should mention the platform
        assert platform in voice.lower()


def test_get_hashtag_strategy(brand_voice):
    """Test getting hashtag strategy"""
    strategy = brand_voice.get_hashtag_strategy()

    assert isinstance(strategy, dict)
    assert "preferred_categories" in strategy
    assert "avoid" in strategy


def test_get_cta_preferences(brand_voice):
    """Test getting call-to-action preferences"""
    cta = brand_voice.get_cta_preferences()

    assert isinstance(cta, dict)
    assert "preferred" in cta
    assert "avoid" in cta


def test_get_values(brand_voice):
    """Test getting brand values"""
    values = brand_voice.get_values()

    assert isinstance(values, list)
    assert len(values) > 0
    assert all(isinstance(v, str) for v in values)


def test_get_avoidances(brand_voice):
    """Test getting things to avoid"""
    avoid = brand_voice.get_avoidances()

    assert isinstance(avoid, dict)
    # Should have language and/or topics to avoid
    assert "language" in avoid or "topics" in avoid


def test_get_platform_focus(brand_voice):
    """Test getting platform-specific focus"""
    linkedin_focus = brand_voice.get_platform_focus("linkedin")

    assert isinstance(linkedin_focus, str)
    # LinkedIn should focus on professional content
    assert any(
        keyword in linkedin_focus.lower()
        for keyword in ["professional", "industry", "thought", "insight"]
    )


def test_get_platform_style(brand_voice):
    """Test getting platform-specific style"""
    twitter_style = brand_voice.get_platform_style("twitter")

    assert isinstance(twitter_style, str)
    # Twitter should have casual/conversational style
    assert any(keyword in twitter_style.lower() for keyword in ["casual", "conversational"])


def test_generate_hashtags_basic(brand_voice):
    """Test basic hashtag generation"""
    hashtags = brand_voice.generate_hashtags("linkedin", "AI innovation product launch", count=3)

    assert isinstance(hashtags, list)
    assert len(hashtags) <= 3
    assert all(isinstance(tag, str) for tag in hashtags)


def test_generate_hashtags_respects_platform_limit(brand_voice):
    """Test that hashtag generation respects platform limits"""
    # LinkedIn allows up to 5 hashtags
    hashtags = brand_voice.generate_hashtags("linkedin", "test topic")
    assert len(hashtags) <= 5

    # Twitter allows up to 2 hashtags
    hashtags = brand_voice.generate_hashtags("twitter", "test topic")
    assert len(hashtags) <= 2


def test_format_hashtags(brand_voice):
    """Test hashtag formatting"""
    hashtags = ["Innovation", "Technology", "Business"]
    formatted = brand_voice.format_hashtags(hashtags)

    assert isinstance(formatted, str)
    assert "#Innovation" in formatted
    assert "#Technology" in formatted
    assert "#Business" in formatted


def test_format_hashtags_no_double_hash(brand_voice):
    """Test that formatting doesn't add double # if already present"""
    hashtags = ["#Innovation", "Technology"]
    formatted = brand_voice.format_hashtags(hashtags)

    # Should not have ##
    assert "##" not in formatted
    assert "#Innovation" in formatted
    assert "#Technology" in formatted


def test_invalid_guidelines_path():
    """Test that invalid path raises error"""
    with pytest.raises(FileNotFoundError):
        BrandVoice(guidelines_path="/nonexistent/path/guidelines.yaml")


def test_invalid_yaml_content(tmp_path):
    """Test that invalid YAML content raises proper error"""
    # Create a temporary invalid YAML file
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("{ invalid yaml content: [not closed")

    with pytest.raises(ValueError, match="Invalid YAML"):
        BrandVoice(guidelines_path=str(invalid_yaml))


def test_non_dict_yaml_content(tmp_path):
    """Test that non-dictionary YAML raises proper error"""
    # Create a YAML file with a list instead of dict
    list_yaml = tmp_path / "list.yaml"
    list_yaml.write_text("- item1\n- item2\n- item3")

    with pytest.raises(ValueError, match="must be a YAML dictionary"):
        BrandVoice(guidelines_path=str(list_yaml))


def test_error_handling_robustness():
    """Test that brand voice handles missing keys gracefully"""
    # Test with actual guidelines file that should exist
    brand_voice = BrandVoice()

    # These methods should not raise errors even if keys are missing
    voice = brand_voice.get_brand_voice("nonexistent_platform")
    assert isinstance(voice, str)

    strategy = brand_voice.get_hashtag_strategy()
    assert isinstance(strategy, dict)

    values = brand_voice.get_values()
    assert isinstance(values, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
