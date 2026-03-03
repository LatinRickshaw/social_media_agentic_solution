"""
Unit tests for SOC-22 FastAPI REST service.

All tests use TestClient with a mocked SocialMediaGenerator so no live API
keys are needed and no SDK clients are instantiated.

Coverage:
  - GET /health returns {"status": "ok"}
  - GET /providers returns text and image provider lists
  - POST /generate with a single platform returns a keyed-by-platform dict
  - POST /generate with platform="all" calls generate_all_platforms
  - POST /generate with provider overrides passes the correct ProviderConfig
  - POST /generate with an invalid provider name returns 422
  - POST /generate with an invalid platform returns 422
  - POST /generate with a missing prompt returns 422
"""

from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_FAKE_POST: Dict = {
    "content": "Great post content",
    "hashtags": ["Innovation"],
    "image_path": "generated_images/linkedin_20260303.png",
    "image_prompt": "A professional image",
    "platform": "linkedin",
    "metadata": {
        "char_count": 18,
        "char_limit": 3000,
        "image_size": [1200, 627],
        "brand_voice": "professional",
        "timestamp": "2026-03-03T00:00:00",
    },
}


@pytest.fixture
def mock_generator():
    """Patch SocialMediaGenerator in the app module for the duration of a test."""
    with patch("src.api.app.SocialMediaGenerator") as MockClass:
        instance = MagicMock()
        instance.generate_post.return_value = _FAKE_POST
        instance.generate_all_platforms.return_value = {
            "linkedin": _FAKE_POST,
            "twitter": _FAKE_POST,
            "facebook": _FAKE_POST,
            "nextdoor": _FAKE_POST,
        }
        MockClass.return_value = instance
        yield instance


@pytest.fixture
def mock_default_config():
    """Patch Config.default_provider_config to avoid requiring API keys."""
    with patch("src.api.app.Config.default_provider_config") as mock_cfg:
        mock_cfg.return_value = MagicMock()
        yield mock_cfg


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /providers
# ---------------------------------------------------------------------------


class TestProviders:
    def test_returns_text_and_image_keys(self):
        response = client.get("/providers")
        assert response.status_code == 200
        body = response.json()
        assert "text" in body
        assert "image" in body

    def test_text_providers_are_list(self):
        body = client.get("/providers").json()
        assert isinstance(body["text"], list)
        assert len(body["text"]) > 0

    def test_image_providers_are_list(self):
        body = client.get("/providers").json()
        assert isinstance(body["image"], list)
        assert len(body["image"]) > 0

    def test_known_text_providers_present(self):
        body = client.get("/providers").json()
        for name in ("anthropic", "openai", "gemini"):
            assert name in body["text"]

    def test_known_image_providers_present(self):
        body = client.get("/providers").json()
        for name in ("gemini", "openai"):
            assert name in body["image"]


# ---------------------------------------------------------------------------
# POST /generate — single platform
# ---------------------------------------------------------------------------


class TestGenerateSinglePlatform:
    def test_returns_200_with_posts_key(self, mock_generator, mock_default_config):
        response = client.post(
            "/generate",
            json={"prompt": "New product launch", "platform": "linkedin"},
        )
        assert response.status_code == 200
        assert "posts" in response.json()

    def test_result_keyed_by_platform(self, mock_generator, mock_default_config):
        response = client.post(
            "/generate",
            json={"prompt": "New product launch", "platform": "linkedin"},
        )
        posts = response.json()["posts"]
        assert "linkedin" in posts

    def test_calls_generate_post_with_correct_args(self, mock_generator, mock_default_config):
        client.post(
            "/generate",
            json={"prompt": "Team update", "platform": "twitter"},
        )
        mock_generator.generate_post.assert_called_once_with("Team update", "twitter")

    def test_all_platforms_accepted(self, mock_generator, mock_default_config):
        for platform in ("linkedin", "twitter", "facebook", "nextdoor"):
            response = client.post(
                "/generate",
                json={"prompt": "Post", "platform": platform},
            )
            assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /generate — all platforms
# ---------------------------------------------------------------------------


class TestGenerateAllPlatforms:
    def test_calls_generate_all_platforms(self, mock_generator, mock_default_config):
        client.post(
            "/generate",
            json={"prompt": "Company news", "platform": "all"},
        )
        mock_generator.generate_all_platforms.assert_called_once_with("Company news")

    def test_response_contains_all_four_platforms(self, mock_generator, mock_default_config):
        response = client.post(
            "/generate",
            json={"prompt": "Company news", "platform": "all"},
        )
        posts = response.json()["posts"]
        for platform in ("linkedin", "twitter", "facebook", "nextdoor"):
            assert platform in posts


# ---------------------------------------------------------------------------
# POST /generate — provider overrides
# ---------------------------------------------------------------------------


class TestGenerateProviderOverrides:
    def test_content_override_used(self, mock_default_config):
        with patch("src.api.app.get_text_provider") as mock_text, patch(
            "src.api.app.SocialMediaGenerator"
        ) as MockGen:
            mock_text.return_value = MagicMock()
            instance = MagicMock()
            instance.generate_post.return_value = _FAKE_POST
            MockGen.return_value = instance

            client.post(
                "/generate",
                json={
                    "prompt": "Launch",
                    "platform": "linkedin",
                    "providers": {"content": "anthropic"},
                },
            )

            # get_text_provider should have been called with "anthropic"
            mock_text.assert_any_call("anthropic")

    def test_image_override_used(self, mock_default_config):
        with patch("src.api.app.get_image_provider") as mock_img, patch(
            "src.api.app.SocialMediaGenerator"
        ) as MockGen:
            mock_img.return_value = MagicMock()
            instance = MagicMock()
            instance.generate_post.return_value = _FAKE_POST
            MockGen.return_value = instance

            client.post(
                "/generate",
                json={
                    "prompt": "Launch",
                    "platform": "linkedin",
                    "providers": {"image": "openai"},
                },
            )

            mock_img.assert_any_call("openai")


# ---------------------------------------------------------------------------
# POST /generate — validation errors (HTTP 422)
# ---------------------------------------------------------------------------


class TestGenerateValidation:
    def test_invalid_text_provider_returns_422(self):
        response = client.post(
            "/generate",
            json={
                "prompt": "Test",
                "platform": "linkedin",
                "providers": {"content": "unknown_provider"},
            },
        )
        assert response.status_code == 422

    def test_invalid_image_provider_returns_422(self):
        response = client.post(
            "/generate",
            json={
                "prompt": "Test",
                "platform": "linkedin",
                "providers": {"image": "unknown_provider"},
            },
        )
        assert response.status_code == 422

    def test_invalid_platform_returns_422(self):
        response = client.post(
            "/generate",
            json={"prompt": "Test", "platform": "tiktok"},
        )
        assert response.status_code == 422

    def test_missing_prompt_returns_422(self):
        response = client.post(
            "/generate",
            json={"platform": "linkedin"},
        )
        assert response.status_code == 422

    def test_missing_platform_returns_422(self):
        response = client.post(
            "/generate",
            json={"prompt": "Test"},
        )
        assert response.status_code == 422

    def test_422_body_contains_detail(self):
        response = client.post(
            "/generate",
            json={
                "prompt": "Test",
                "platform": "linkedin",
                "providers": {"content": "bad_provider"},
            },
        )
        assert "detail" in response.json()
