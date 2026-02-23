"""
Unit tests for SOC-17 text provider implementations.

All three providers are tested with mocked SDK clients so no live API keys
are required. Each test class covers:

  - ValueError raised when API key is absent or empty
  - generate_text() delegates to the correct SDK method
  - generate_text() extracts and returns the correct string value
  - generate_text() forwards all parameters correctly
  - Custom api_key / model values override Config defaults
  - Package-level import path works
"""

from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# AnthropicTextProvider tests
# ---------------------------------------------------------------------------


class TestAnthropicTextProvider:
    def _make_provider(self, api_key: str = "test-key", model: str = "claude-opus-4-6"):
        """Create a provider with a mocked Anthropic client."""
        with patch("src.core.providers.anthropic.anthropic.Anthropic") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from src.core.providers.anthropic import AnthropicTextProvider

            provider = AnthropicTextProvider(api_key=api_key, model=model)
            provider._client = mock_client
            return provider, mock_client

    def test_raises_when_api_key_empty(self):
        from src.core.providers.anthropic import AnthropicTextProvider

        with pytest.raises(ValueError, match="Anthropic API key"):
            AnthropicTextProvider(api_key="")

    def test_raises_when_api_key_none_and_config_unset(self):
        from src.core.providers.anthropic import AnthropicTextProvider
        from src.core.config import Config

        with patch.object(Config, "ANTHROPIC_API_KEY", None):
            with pytest.raises(ValueError, match="Anthropic API key"):
                AnthropicTextProvider()

    def test_instantiates_with_valid_key(self):
        from src.core.providers.anthropic import AnthropicTextProvider
        from src.core.providers.base import TextProvider

        with patch("src.core.providers.anthropic.anthropic.Anthropic"):
            provider = AnthropicTextProvider(api_key="test-key")
            assert isinstance(provider, TextProvider)

    def test_generate_text_returns_string(self):
        provider, mock_client = self._make_provider()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="hello world")]
        mock_client.messages.create.return_value = mock_response

        result = provider.generate_text("sys", "user prompt", 100, 0.7)
        assert result == "hello world"

    def test_generate_text_calls_messages_create_with_correct_args(self):
        provider, mock_client = self._make_provider(model="claude-opus-4-6")
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="output")]
        mock_client.messages.create.return_value = mock_response

        provider.generate_text(
            system="be helpful",
            prompt="write a post",
            max_tokens=256,
            temperature=0.5,
        )

        mock_client.messages.create.assert_called_once_with(
            model="claude-opus-4-6",
            system="be helpful",
            messages=[{"role": "user", "content": "write a post"}],
            max_tokens=256,
            temperature=0.5,
        )

    def test_custom_model_is_used(self):
        provider, mock_client = self._make_provider(model="claude-haiku-4-5-20251001")
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ok")]
        mock_client.messages.create.return_value = mock_response

        provider.generate_text("s", "p", 50, 0.3)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

    def test_config_default_model_used_when_none_supplied(self):
        from src.core.config import Config

        with patch("src.core.providers.anthropic.anthropic.Anthropic"):
            from src.core.providers.anthropic import AnthropicTextProvider

            provider = AnthropicTextProvider(api_key="test-key")
            assert provider._model == Config.ANTHROPIC_MODEL


# ---------------------------------------------------------------------------
# OpenAITextProvider tests
# ---------------------------------------------------------------------------


class TestOpenAITextProvider:
    def _make_provider(self, api_key: str = "test-key", model: str = "gpt-4"):
        """Create a provider with a mocked OpenAI client."""
        with patch("src.core.providers.openai_text.openai.OpenAI") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from src.core.providers.openai_text import OpenAITextProvider

            provider = OpenAITextProvider(api_key=api_key, model=model)
            provider._client = mock_client
            return provider, mock_client

    def test_raises_when_api_key_empty(self):
        from src.core.providers.openai_text import OpenAITextProvider

        with pytest.raises(ValueError, match="OpenAI API key"):
            OpenAITextProvider(api_key="")

    def test_raises_when_api_key_none_and_config_unset(self):
        from src.core.providers.openai_text import OpenAITextProvider
        from src.core.config import Config

        with patch.object(Config, "OPENAI_API_KEY", None):
            with pytest.raises(ValueError, match="OpenAI API key"):
                OpenAITextProvider()

    def test_instantiates_with_valid_key(self):
        from src.core.providers.openai_text import OpenAITextProvider
        from src.core.providers.base import TextProvider

        with patch("src.core.providers.openai_text.openai.OpenAI"):
            provider = OpenAITextProvider(api_key="test-key")
            assert isinstance(provider, TextProvider)

    def test_generate_text_returns_string(self):
        provider, mock_client = self._make_provider()
        mock_choice = MagicMock()
        mock_choice.message.content = "generated text"
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        result = provider.generate_text("sys", "prompt", 100, 0.7)
        assert result == "generated text"

    def test_generate_text_calls_chat_completions_with_correct_args(self):
        provider, mock_client = self._make_provider(model="gpt-4")
        mock_choice = MagicMock()
        mock_choice.message.content = "out"
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        provider.generate_text(
            system="you are helpful",
            prompt="write something",
            max_tokens=512,
            temperature=0.9,
        )

        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "you are helpful"},
                {"role": "user", "content": "write something"},
            ],
            max_tokens=512,
            temperature=0.9,
        )

    def test_custom_model_is_used(self):
        provider, mock_client = self._make_provider(model="gpt-4o")
        mock_choice = MagicMock()
        mock_choice.message.content = "ok"
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        provider.generate_text("s", "p", 50, 0.1)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o"

    def test_config_default_model_used_when_none_supplied(self):
        from src.core.config import Config

        with patch("src.core.providers.openai_text.openai.OpenAI"):
            from src.core.providers.openai_text import OpenAITextProvider

            provider = OpenAITextProvider(api_key="test-key")
            assert provider._model == Config.OPENAI_MODEL


# ---------------------------------------------------------------------------
# GeminiTextProvider tests
# ---------------------------------------------------------------------------


class TestGeminiTextProvider:
    def _make_provider(self, api_key: str = "test-key", model: str = "gemini-2.0-flash"):
        """Create a provider with a mocked Gemini client."""
        with patch("src.core.providers.gemini_text.genai.Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from src.core.providers.gemini_text import GeminiTextProvider

            provider = GeminiTextProvider(api_key=api_key, model=model)
            provider._client = mock_client
            return provider, mock_client

    def test_raises_when_api_key_empty(self):
        from src.core.providers.gemini_text import GeminiTextProvider

        with pytest.raises(ValueError, match="Google API key"):
            GeminiTextProvider(api_key="")

    def test_raises_when_api_key_none_and_config_unset(self):
        from src.core.providers.gemini_text import GeminiTextProvider
        from src.core.config import Config

        with patch.object(Config, "GOOGLE_API_KEY", None):
            with pytest.raises(ValueError, match="Google API key"):
                GeminiTextProvider()

    def test_instantiates_with_valid_key(self):
        from src.core.providers.gemini_text import GeminiTextProvider
        from src.core.providers.base import TextProvider

        with patch("src.core.providers.gemini_text.genai.Client"):
            provider = GeminiTextProvider(api_key="test-key")
            assert isinstance(provider, TextProvider)

    def test_generate_text_returns_string(self):
        provider, mock_client = self._make_provider()
        mock_response = MagicMock()
        mock_response.text = "gemini response"
        mock_client.models.generate_content.return_value = mock_response

        result = provider.generate_text("sys", "prompt", 100, 0.7)
        assert result == "gemini response"

    def test_generate_text_calls_generate_content_with_correct_args(self):
        provider, mock_client = self._make_provider(model="gemini-2.0-flash")
        mock_response = MagicMock()
        mock_response.text = "out"
        mock_client.models.generate_content.return_value = mock_response

        provider.generate_text(
            system="be concise",
            prompt="describe the sky",
            max_tokens=200,
            temperature=0.4,
        )

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.0-flash"
        assert call_kwargs["contents"] == "describe the sky"
        cfg = call_kwargs["config"]
        assert cfg.system_instruction == "be concise"
        assert cfg.temperature == 0.4
        assert cfg.max_output_tokens == 200

    def test_custom_model_is_used(self):
        provider, mock_client = self._make_provider(model="gemini-1.5-pro")
        mock_response = MagicMock()
        mock_response.text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        provider.generate_text("s", "p", 50, 0.2)

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-1.5-pro"

    def test_config_default_model_used_when_none_supplied(self):
        from src.core.config import Config

        with patch("src.core.providers.gemini_text.genai.Client"):
            from src.core.providers.gemini_text import GeminiTextProvider

            provider = GeminiTextProvider(api_key="test-key")
            assert provider._model == Config.GEMINI_TEXT_MODEL


# ---------------------------------------------------------------------------
# Import path tests (acceptance criteria)
# ---------------------------------------------------------------------------


class TestImportPaths:
    def test_import_from_modules(self):
        from src.core.providers.anthropic import AnthropicTextProvider  # noqa: F401
        from src.core.providers.openai_text import OpenAITextProvider  # noqa: F401
        from src.core.providers.gemini_text import GeminiTextProvider  # noqa: F401

    def test_import_from_package(self):
        from src.core.providers import AnthropicTextProvider  # noqa: F401
        from src.core.providers import OpenAITextProvider  # noqa: F401
        from src.core.providers import GeminiTextProvider  # noqa: F401

    def test_all_are_text_providers(self):
        from src.core.providers.base import TextProvider
        from src.core.providers.anthropic import AnthropicTextProvider
        from src.core.providers.openai_text import OpenAITextProvider
        from src.core.providers.gemini_text import GeminiTextProvider

        assert issubclass(AnthropicTextProvider, TextProvider)
        assert issubclass(OpenAITextProvider, TextProvider)
        assert issubclass(GeminiTextProvider, TextProvider)
