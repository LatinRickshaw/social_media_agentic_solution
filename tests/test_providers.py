"""
Tests for provider configuration wiring (SOC-24).

The split test files already cover each provider in isolation:
  - test_providers_base.py   → TextProvider, ImageProvider ABCs, ProviderConfig
  - test_text_providers.py   → AnthropicTextProvider, OpenAITextProvider, GeminiTextProvider
  - test_image_providers.py  → GeminiImageProvider, OpenAIImageProvider
  - test_registry.py         → get_text_provider, get_image_provider, list_providers

This file tests the top-level wiring layer — Config.default_provider_config() and
Config.validate() — which were not covered in isolation by the split files.

Coverage:
  - Config.default_provider_config() returns a correctly-populated ProviderConfig
  - All four ProviderConfig fields are populated (not None)
  - Text fields receive a TextProvider; image field receives an ImageProvider
  - DEFAULT_*_PROVIDER env vars control which provider name reaches the registry
  - get_text_provider called three times (content, hashtags, image_prompt roles)
  - get_image_provider called once (image role)
  - Config.validate() returns a dict with expected keys and bool values
  - validate() correctly reflects presence/absence of API keys per configured provider
"""

from unittest.mock import MagicMock, patch

from src.core.config import Config
from src.core.providers.base import ImageProvider, ProviderConfig, TextProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text_mock() -> MagicMock:
    return MagicMock(spec=TextProvider)


def _image_mock() -> MagicMock:
    return MagicMock(spec=ImageProvider)


# ---------------------------------------------------------------------------
# Config.default_provider_config
# ---------------------------------------------------------------------------


class TestDefaultProviderConfig:
    def test_returns_provider_config_instance(self):
        with (
            patch("src.core.providers.registry.get_text_provider", return_value=_text_mock()),
            patch("src.core.providers.registry.get_image_provider", return_value=_image_mock()),
        ):
            config = Config.default_provider_config()
        assert isinstance(config, ProviderConfig)

    def test_all_four_fields_populated(self):
        with (
            patch("src.core.providers.registry.get_text_provider", return_value=_text_mock()),
            patch("src.core.providers.registry.get_image_provider", return_value=_image_mock()),
        ):
            config = Config.default_provider_config()
        assert config.content is not None
        assert config.hashtags is not None
        assert config.image_prompt is not None
        assert config.image is not None

    def test_text_fields_receive_text_provider(self):
        mock_text = _text_mock()
        with (
            patch("src.core.providers.registry.get_text_provider", return_value=mock_text),
            patch("src.core.providers.registry.get_image_provider", return_value=_image_mock()),
        ):
            config = Config.default_provider_config()
        assert config.content is mock_text
        assert config.hashtags is mock_text
        assert config.image_prompt is mock_text

    def test_image_field_receives_image_provider(self):
        mock_image = _image_mock()
        with (
            patch("src.core.providers.registry.get_text_provider", return_value=_text_mock()),
            patch("src.core.providers.registry.get_image_provider", return_value=mock_image),
        ):
            config = Config.default_provider_config()
        assert config.image is mock_image

    def test_get_text_provider_called_three_times(self):
        with (
            patch(
                "src.core.providers.registry.get_text_provider", return_value=_text_mock()
            ) as mock_gtp,
            patch("src.core.providers.registry.get_image_provider", return_value=_image_mock()),
        ):
            Config.default_provider_config()
        assert mock_gtp.call_count == 3

    def test_get_image_provider_called_once(self):
        with (
            patch("src.core.providers.registry.get_text_provider", return_value=_text_mock()),
            patch(
                "src.core.providers.registry.get_image_provider", return_value=_image_mock()
            ) as mock_gip,
        ):
            Config.default_provider_config()
        assert mock_gip.call_count == 1

    def test_content_provider_name_forwarded_to_registry(self):
        with (
            patch.object(Config, "DEFAULT_CONTENT_PROVIDER", "anthropic"),
            patch(
                "src.core.providers.registry.get_text_provider", return_value=_text_mock()
            ) as mock_gtp,
            patch("src.core.providers.registry.get_image_provider", return_value=_image_mock()),
        ):
            Config.default_provider_config()
        called_names = [c.args[0] for c in mock_gtp.call_args_list]
        assert "anthropic" in called_names

    def test_image_provider_name_forwarded_to_registry(self):
        with (
            patch.object(Config, "DEFAULT_IMAGE_PROVIDER", "openai"),
            patch("src.core.providers.registry.get_text_provider", return_value=_text_mock()),
            patch(
                "src.core.providers.registry.get_image_provider", return_value=_image_mock()
            ) as mock_gip,
        ):
            Config.default_provider_config()
        mock_gip.assert_called_once_with("openai")


# ---------------------------------------------------------------------------
# Config.validate
# ---------------------------------------------------------------------------


class TestConfigValidate:
    def test_returns_dict_with_expected_keys(self):
        result = Config.validate()
        assert set(result.keys()) == {"text_providers", "image_provider", "database"}

    def test_all_values_are_bool(self):
        result = Config.validate()
        for value in result.values():
            assert isinstance(value, bool)

    def test_text_providers_false_when_key_missing(self):
        with (
            patch.object(Config, "OPENAI_API_KEY", None),
            patch.object(Config, "DEFAULT_CONTENT_PROVIDER", "openai"),
            patch.object(Config, "DEFAULT_HASHTAG_PROVIDER", "openai"),
            patch.object(Config, "DEFAULT_IMAGE_PROMPT_PROVIDER", "openai"),
        ):
            result = Config.validate()
        assert result["text_providers"] is False

    def test_text_providers_true_when_key_present(self):
        with (
            patch.object(Config, "OPENAI_API_KEY", "sk-test"),
            patch.object(Config, "DEFAULT_CONTENT_PROVIDER", "openai"),
            patch.object(Config, "DEFAULT_HASHTAG_PROVIDER", "openai"),
            patch.object(Config, "DEFAULT_IMAGE_PROMPT_PROVIDER", "openai"),
        ):
            result = Config.validate()
        assert result["text_providers"] is True

    def test_image_provider_false_when_key_missing(self):
        with (
            patch.object(Config, "OPENAI_API_KEY", None),
            patch.object(Config, "DEFAULT_IMAGE_PROVIDER", "openai"),
        ):
            result = Config.validate()
        assert result["image_provider"] is False

    def test_image_provider_true_when_key_present(self):
        with (
            patch.object(Config, "GOOGLE_API_KEY", "ai-test"),
            patch.object(Config, "DEFAULT_IMAGE_PROVIDER", "gemini"),
        ):
            result = Config.validate()
        assert result["image_provider"] is True

    def test_database_false_when_password_missing(self):
        with patch.object(Config, "DB_PASSWORD", None):
            result = Config.validate()
        assert result["database"] is False

    def test_database_true_when_password_present(self):
        with patch.object(Config, "DB_PASSWORD", "secret"):
            result = Config.validate()
        assert result["database"] is True
