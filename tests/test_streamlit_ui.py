"""
Integration tests for Streamlit UI components.

Tests the integration between UI helper functions and core services.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import UI functions to test
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import PLATFORM_SPECS  # noqa: E402
from src.ui.streamlit_app import (  # noqa: E402
    get_character_count_status,
    initialize_session_state,
)


class TestCharacterCounter:
    """Test character count validation logic"""

    def test_character_count_ok(self):
        """Test character count within limits"""
        count, status = get_character_count_status("Hello World", 100)
        assert count == 11
        assert status == "ok"

    def test_character_count_warning(self):
        """Test character count near limit (90%+)"""
        content = "x" * 91  # 91 chars for limit of 100
        count, status = get_character_count_status(content, 100)
        assert count == 91
        assert status == "warning"

    def test_character_count_error(self):
        """Test character count exceeds limit"""
        content = "x" * 101  # 101 chars for limit of 100
        count, status = get_character_count_status(content, 100)
        assert count == 101
        assert status == "error"

    def test_twitter_character_limit(self):
        """Test with actual Twitter limit"""
        content = "x" * 280
        count, status = get_character_count_status(content, PLATFORM_SPECS["twitter"]["char_limit"])
        assert count == 280
        assert status == "ok"

    def test_linkedin_character_limit(self):
        """Test with actual LinkedIn limit"""
        content = "x" * 3000
        count, status = get_character_count_status(
            content, PLATFORM_SPECS["linkedin"]["char_limit"]
        )
        assert count == 3000
        assert status == "ok"


class TestSessionState:
    """Test session state initialization"""

    @patch("src.ui.streamlit_app.st")
    def test_initialize_session_state(self, mock_st):
        """Test session state variables are initialized correctly"""

        # Use a class that supports both attribute access and 'in' operator
        class MockSessionState:
            def __contains__(self, key):
                return hasattr(self, key)

            def __getitem__(self, key):
                return getattr(self, key)

            def __setitem__(self, key, value):
                setattr(self, key, value)

        mock_st.session_state = MockSessionState()

        initialize_session_state()

        # Verify all required keys are initialized
        assert "generated_posts" in mock_st.session_state
        assert "generator" in mock_st.session_state
        assert "brand_voice" in mock_st.session_state
        assert "generation_in_progress" in mock_st.session_state

        # Verify types
        assert isinstance(mock_st.session_state["generated_posts"], dict)
        assert mock_st.session_state["generation_in_progress"] is False

    @patch("src.ui.streamlit_app.st")
    def test_initialize_session_state_idempotent(self, mock_st):
        """Test that re-initialization doesn't reset state"""
        # Setup existing state
        mock_st.session_state = {
            "generated_posts": {"linkedin": {"content": "test"}},
            "generator": Mock(),
            "brand_voice": Mock(),
            "generation_in_progress": True,
        }

        # Store references to verify they don't change
        original_posts = mock_st.session_state["generated_posts"]
        original_generator = mock_st.session_state["generator"]

        initialize_session_state()

        # Verify state wasn't reset
        assert mock_st.session_state["generated_posts"] is original_posts
        assert mock_st.session_state["generator"] is original_generator
        assert mock_st.session_state["generation_in_progress"] is True


class TestPlatformIntegration:
    """Test integration with existing platform specifications"""

    def test_all_platforms_have_char_limits(self):
        """Verify all platforms have character limits defined"""
        for platform, specs in PLATFORM_SPECS.items():
            assert "char_limit" in specs
            assert isinstance(specs["char_limit"], int)
            assert specs["char_limit"] > 0

    def test_all_platforms_have_image_sizes(self):
        """Verify all platforms have image size specifications"""
        for platform, specs in PLATFORM_SPECS.items():
            assert "image_size" in specs
            assert isinstance(specs["image_size"], tuple)
            assert len(specs["image_size"]) == 2
            assert all(isinstance(dim, int) for dim in specs["image_size"])

    def test_all_platforms_have_hashtag_limits(self):
        """Verify all platforms have hashtag limits defined"""
        for platform, specs in PLATFORM_SPECS.items():
            assert "max_hashtags" in specs
            assert isinstance(specs["max_hashtags"], int)
            assert specs["max_hashtags"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
