"""
Unit tests for SOC-18 image provider implementations.

Both providers are tested with mocked SDK clients so no live API keys
are required. Each test class covers:

  - ValueError raised when API key is absent or empty
  - generate_image() delegates to the correct SDK method
  - generate_image() returns raw bytes
  - generate_image() forwards all parameters correctly
  - Custom api_key / model values override Config defaults
  - Package-level import path works
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# GeminiImageProvider tests
# ---------------------------------------------------------------------------


class TestGeminiImageProvider:
    def _make_provider(self, api_key: str = "test-key", model: str = "imagen-3.0-generate-001"):
        """Create a provider with a mocked Gemini client."""
        with patch("src.core.providers.gemini_image.genai.Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from src.core.providers.gemini_image import GeminiImageProvider

            provider = GeminiImageProvider(api_key=api_key, model=model)
            provider._client = mock_client
            return provider, mock_client

    def test_raises_when_api_key_empty(self):
        from src.core.providers.gemini_image import GeminiImageProvider

        with pytest.raises(ValueError, match="Google API key"):
            GeminiImageProvider(api_key="")

    def test_raises_when_api_key_none_and_config_unset(self):
        from src.core.providers.gemini_image import GeminiImageProvider
        from src.core.config import Config

        with patch.object(Config, "GOOGLE_API_KEY", None):
            with pytest.raises(ValueError, match="Google API key"):
                GeminiImageProvider()

    def test_instantiates_with_valid_key(self):
        from src.core.providers.gemini_image import GeminiImageProvider
        from src.core.providers.base import ImageProvider

        with patch("src.core.providers.gemini_image.genai.Client"):
            provider = GeminiImageProvider(api_key="test-key")
            assert isinstance(provider, ImageProvider)

    def test_generate_image_returns_bytes(self):
        provider, mock_client = self._make_provider()
        expected_bytes = b"\x89PNG\r\nfake-image-data"
        mock_image = MagicMock()
        mock_image.image.image_bytes = expected_bytes
        mock_client.models.generate_images.return_value = MagicMock(generated_images=[mock_image])

        result = provider.generate_image("a sunset", 1200, 627)
        assert result == expected_bytes

    def test_generate_image_calls_generate_images_with_correct_model(self):
        provider, mock_client = self._make_provider(model="imagen-3.0-generate-001")
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"bytes"
        mock_client.models.generate_images.return_value = MagicMock(generated_images=[mock_image])

        provider.generate_image("test prompt", 1200, 627)

        call_kwargs = mock_client.models.generate_images.call_args.kwargs
        assert call_kwargs["model"] == "imagen-3.0-generate-001"
        assert call_kwargs["prompt"] == "test prompt"

    def test_generate_image_requests_one_image(self):
        provider, mock_client = self._make_provider()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"bytes"
        mock_client.models.generate_images.return_value = MagicMock(generated_images=[mock_image])

        provider.generate_image("prompt", 800, 600)

        call_kwargs = mock_client.models.generate_images.call_args.kwargs
        assert call_kwargs["config"].number_of_images == 1

    def test_custom_model_is_used(self):
        provider, mock_client = self._make_provider(model="imagen-3.0-fast-generate-001")
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"bytes"
        mock_client.models.generate_images.return_value = MagicMock(generated_images=[mock_image])

        provider.generate_image("p", 100, 100)

        call_kwargs = mock_client.models.generate_images.call_args.kwargs
        assert call_kwargs["model"] == "imagen-3.0-fast-generate-001"

    def test_config_default_model_used_when_none_supplied(self):
        from src.core.config import Config

        with patch("src.core.providers.gemini_image.genai.Client"):
            from src.core.providers.gemini_image import GeminiImageProvider

            provider = GeminiImageProvider(api_key="test-key")
            assert provider._model == Config.GEMINI_IMAGE_MODEL


# ---------------------------------------------------------------------------
# OpenAIImageProvider tests
# ---------------------------------------------------------------------------


class TestOpenAIImageProvider:
    def _make_provider(self, api_key: str = "test-key", model: str = "dall-e-3"):
        """Create a provider with a mocked OpenAI client."""
        with patch("src.core.providers.openai_image.openai.OpenAI") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from src.core.providers.openai_image import OpenAIImageProvider

            provider = OpenAIImageProvider(api_key=api_key, model=model)
            provider._client = mock_client
            return provider, mock_client

    def test_raises_when_api_key_empty(self):
        from src.core.providers.openai_image import OpenAIImageProvider

        with pytest.raises(ValueError, match="OpenAI API key"):
            OpenAIImageProvider(api_key="")

    def test_raises_when_api_key_none_and_config_unset(self):
        from src.core.providers.openai_image import OpenAIImageProvider
        from src.core.config import Config

        with patch.object(Config, "OPENAI_API_KEY", None):
            with pytest.raises(ValueError, match="OpenAI API key"):
                OpenAIImageProvider()

    def test_instantiates_with_valid_key(self):
        from src.core.providers.openai_image import OpenAIImageProvider
        from src.core.providers.base import ImageProvider

        with patch("src.core.providers.openai_image.openai.OpenAI"):
            provider = OpenAIImageProvider(api_key="test-key")
            assert isinstance(provider, ImageProvider)

    def test_generate_image_returns_downloaded_bytes(self):
        provider, mock_client = self._make_provider()
        expected_bytes = b"\x89PNG\r\nfake-image"
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/img.png")]
        )

        with patch("src.core.providers.openai_image.requests.get") as mock_get:
            mock_get.return_value = MagicMock(content=expected_bytes)
            result = provider.generate_image("a mountain", 1200, 627)

        assert result == expected_bytes

    def test_generate_image_calls_images_generate_with_correct_args(self):
        provider, mock_client = self._make_provider(model="dall-e-3")
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/img.png")]
        )

        with patch("src.core.providers.openai_image.requests.get") as mock_get:
            mock_get.return_value = MagicMock(content=b"bytes")
            provider.generate_image("a city", 1200, 627)

        mock_client.images.generate.assert_called_once_with(
            model="dall-e-3",
            prompt="a city",
            size="1792x1024",
            response_format="url",
            n=1,
        )

    def test_downloads_from_url_returned_by_api(self):
        provider, mock_client = self._make_provider()
        test_url = "https://example.com/generated.png"
        mock_client.images.generate.return_value = MagicMock(data=[MagicMock(url=test_url)])

        with patch("src.core.providers.openai_image.requests.get") as mock_get:
            mock_get.return_value = MagicMock(content=b"bytes")
            provider.generate_image("prompt", 1200, 627)
            mock_get.assert_called_once_with(test_url, timeout=30)

    def test_raises_on_http_error_from_download(self):
        import requests as req

        provider, mock_client = self._make_provider()
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/img.png")]
        )

        with patch("src.core.providers.openai_image.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = req.HTTPError("404")
            mock_get.return_value = mock_response

            with pytest.raises(req.HTTPError):
                provider.generate_image("prompt", 1200, 627)

    def test_custom_model_is_used(self):
        provider, mock_client = self._make_provider(model="dall-e-2")
        mock_client.images.generate.return_value = MagicMock(
            data=[MagicMock(url="https://example.com/img.png")]
        )

        with patch("src.core.providers.openai_image.requests.get") as mock_get:
            mock_get.return_value = MagicMock(content=b"bytes")
            provider.generate_image("p", 100, 100)

        call_kwargs = mock_client.images.generate.call_args.kwargs
        assert call_kwargs["model"] == "dall-e-2"

    def test_config_default_model_used_when_none_supplied(self):
        from src.core.config import Config

        with patch("src.core.providers.openai_image.openai.OpenAI"):
            from src.core.providers.openai_image import OpenAIImageProvider

            provider = OpenAIImageProvider(api_key="test-key")
            assert provider._model == Config.OPENAI_IMAGE_MODEL


# ---------------------------------------------------------------------------
# OpenAIImageProvider._derive_size tests
# ---------------------------------------------------------------------------


class TestDeriveSizeMapping:
    def _get_provider(self):
        with patch("src.core.providers.openai_image.openai.OpenAI"):
            from src.core.providers.openai_image import OpenAIImageProvider

            return OpenAIImageProvider(api_key="test-key")

    def test_landscape_returns_1792x1024(self):
        provider = self._get_provider()
        assert provider._derive_size(1200, 627) == "1792x1024"

    def test_portrait_returns_1024x1792(self):
        provider = self._get_provider()
        assert provider._derive_size(627, 1200) == "1024x1792"

    def test_square_returns_1024x1024(self):
        provider = self._get_provider()
        assert provider._derive_size(1024, 1024) == "1024x1024"

    def test_equal_dimensions_returns_square(self):
        provider = self._get_provider()
        assert provider._derive_size(500, 500) == "1024x1024"


# ---------------------------------------------------------------------------
# Import path tests (acceptance criteria)
# ---------------------------------------------------------------------------


class TestImportPaths:
    def test_import_from_modules(self):
        from src.core.providers.gemini_image import GeminiImageProvider  # noqa: F401
        from src.core.providers.openai_image import OpenAIImageProvider  # noqa: F401

    def test_import_from_package(self):
        from src.core.providers import GeminiImageProvider  # noqa: F401
        from src.core.providers import OpenAIImageProvider  # noqa: F401

    def test_all_are_image_providers(self):
        from src.core.providers.base import ImageProvider
        from src.core.providers.gemini_image import GeminiImageProvider
        from src.core.providers.openai_image import OpenAIImageProvider

        assert issubclass(GeminiImageProvider, ImageProvider)
        assert issubclass(OpenAIImageProvider, ImageProvider)
