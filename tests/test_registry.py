"""
Unit tests for SOC-19 provider registry.

All tests use mocked provider constructors so no live API keys are needed.
Cache isolation is achieved via an autouse fixture that uses patch.dict to
clear both module-level cache dicts before each test.

Coverage:
  - Lazy initialisation: importing the registry does not instantiate providers
  - get_text_provider() returns the correct instance and caches it
  - get_text_provider() raises ValueError with informative message for unknown names
  - get_image_provider() returns the correct instance and caches it
  - get_image_provider() raises ValueError with informative message for unknown names
  - list_providers() returns the exact structure specified in the ticket
  - Package-level import path works for all three public functions
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Cache isolation fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_registry_caches():
    """Reset both registry caches before every test in this module."""
    with patch.dict("src.core.providers.registry._text_cache", {}, clear=True), patch.dict(
        "src.core.providers.registry._image_cache", {}, clear=True
    ):
        yield


# ---------------------------------------------------------------------------
# Lazy initialisation
# ---------------------------------------------------------------------------


class TestLazyInit:
    def test_import_does_not_instantiate_providers(self):
        """Importing the registry module must not call any provider __init__."""
        # If any provider were instantiated at import time, it would raise
        # ValueError (missing API keys in the test environment). The import
        # itself is the assertion — reaching here means no instantiation occurred.
        import src.core.providers.registry  # noqa: F401

    def test_caches_are_dicts(self):
        import src.core.providers.registry as reg

        assert isinstance(reg._text_cache, dict)
        assert isinstance(reg._image_cache, dict)


# ---------------------------------------------------------------------------
# get_text_provider
# ---------------------------------------------------------------------------


class TestGetTextProvider:
    def test_returns_instance_for_anthropic(self):
        mock_instance = MagicMock()
        with patch.dict(
            "src.core.providers.registry._TEXT_PROVIDERS",
            {"anthropic": MagicMock(return_value=mock_instance)},
        ):
            from src.core.providers.registry import get_text_provider

            assert get_text_provider("anthropic") is mock_instance

    def test_returns_instance_for_openai(self):
        mock_instance = MagicMock()
        with patch.dict(
            "src.core.providers.registry._TEXT_PROVIDERS",
            {"openai": MagicMock(return_value=mock_instance)},
        ):
            from src.core.providers.registry import get_text_provider

            assert get_text_provider("openai") is mock_instance

    def test_returns_instance_for_gemini(self):
        mock_instance = MagicMock()
        with patch.dict(
            "src.core.providers.registry._TEXT_PROVIDERS",
            {"gemini": MagicMock(return_value=mock_instance)},
        ):
            from src.core.providers.registry import get_text_provider

            assert get_text_provider("gemini") is mock_instance

    def test_caches_instance_on_repeated_calls(self):
        mock_cls = MagicMock()
        with patch.dict("src.core.providers.registry._TEXT_PROVIDERS", {"anthropic": mock_cls}):
            from src.core.providers.registry import get_text_provider

            first = get_text_provider("anthropic")
            second = get_text_provider("anthropic")

        assert first is second
        mock_cls.assert_called_once()

    def test_different_names_return_different_instances(self):
        mock_a, mock_b = MagicMock(), MagicMock()
        overrides = {
            "anthropic": MagicMock(return_value=mock_a),
            "openai": MagicMock(return_value=mock_b),
        }
        with patch.dict("src.core.providers.registry._TEXT_PROVIDERS", overrides):
            from src.core.providers.registry import get_text_provider

            assert get_text_provider("anthropic") is not get_text_provider("openai")

    def test_raises_for_unknown_name(self):
        from src.core.providers.registry import get_text_provider

        with pytest.raises(ValueError, match="Unknown text provider"):
            get_text_provider("unknown")

    def test_error_message_lists_valid_options(self):
        from src.core.providers.registry import get_text_provider

        with pytest.raises(ValueError) as exc_info:
            get_text_provider("nosuchprovider")

        message = str(exc_info.value)
        assert "anthropic" in message
        assert "openai" in message
        assert "gemini" in message

    def test_empty_string_raises_value_error(self):
        from src.core.providers.registry import get_text_provider

        with pytest.raises(ValueError, match="Unknown text provider"):
            get_text_provider("")


# ---------------------------------------------------------------------------
# get_image_provider
# ---------------------------------------------------------------------------


class TestGetImageProvider:
    def test_returns_instance_for_gemini(self):
        mock_instance = MagicMock()
        with patch.dict(
            "src.core.providers.registry._IMAGE_PROVIDERS",
            {"gemini": MagicMock(return_value=mock_instance)},
        ):
            from src.core.providers.registry import get_image_provider

            assert get_image_provider("gemini") is mock_instance

    def test_returns_instance_for_openai(self):
        mock_instance = MagicMock()
        with patch.dict(
            "src.core.providers.registry._IMAGE_PROVIDERS",
            {"openai": MagicMock(return_value=mock_instance)},
        ):
            from src.core.providers.registry import get_image_provider

            assert get_image_provider("openai") is mock_instance

    def test_caches_instance_on_repeated_calls(self):
        mock_cls = MagicMock()
        with patch.dict("src.core.providers.registry._IMAGE_PROVIDERS", {"gemini": mock_cls}):
            from src.core.providers.registry import get_image_provider

            first = get_image_provider("gemini")
            second = get_image_provider("gemini")

        assert first is second
        mock_cls.assert_called_once()

    def test_different_names_return_different_instances(self):
        mock_g, mock_o = MagicMock(), MagicMock()
        overrides = {
            "gemini": MagicMock(return_value=mock_g),
            "openai": MagicMock(return_value=mock_o),
        }
        with patch.dict("src.core.providers.registry._IMAGE_PROVIDERS", overrides):
            from src.core.providers.registry import get_image_provider

            assert get_image_provider("gemini") is not get_image_provider("openai")

    def test_raises_for_unknown_name(self):
        from src.core.providers.registry import get_image_provider

        with pytest.raises(ValueError, match="Unknown image provider"):
            get_image_provider("unknown")

    def test_error_message_lists_valid_options(self):
        from src.core.providers.registry import get_image_provider

        with pytest.raises(ValueError) as exc_info:
            get_image_provider("nosuchprovider")

        message = str(exc_info.value)
        assert "gemini" in message
        assert "openai" in message

    def test_empty_string_raises_value_error(self):
        from src.core.providers.registry import get_image_provider

        with pytest.raises(ValueError, match="Unknown image provider"):
            get_image_provider("")


# ---------------------------------------------------------------------------
# list_providers
# ---------------------------------------------------------------------------


class TestListProviders:
    def test_returns_text_and_image_keys(self):
        from src.core.providers.registry import list_providers

        result = list_providers()
        assert set(result.keys()) == {"text", "image"}

    def test_text_providers_exact_list(self):
        from src.core.providers.registry import list_providers

        assert list_providers()["text"] == ["anthropic", "openai", "gemini"]

    def test_image_providers_exact_list(self):
        from src.core.providers.registry import list_providers

        assert list_providers()["image"] == ["gemini", "openai"]

    def test_returns_new_dict_on_each_call(self):
        from src.core.providers.registry import list_providers

        assert list_providers() is not list_providers()

    def test_text_list_is_a_list(self):
        from src.core.providers.registry import list_providers

        assert isinstance(list_providers()["text"], list)

    def test_image_list_is_a_list(self):
        from src.core.providers.registry import list_providers

        assert isinstance(list_providers()["image"], list)


# ---------------------------------------------------------------------------
# Import paths (acceptance criteria)
# ---------------------------------------------------------------------------


class TestImportPaths:
    def test_import_from_module(self):
        from src.core.providers.registry import get_image_provider  # noqa: F401
        from src.core.providers.registry import get_text_provider  # noqa: F401
        from src.core.providers.registry import list_providers  # noqa: F401

    def test_import_from_package(self):
        from src.core.providers import get_image_provider  # noqa: F401
        from src.core.providers import get_text_provider  # noqa: F401
        from src.core.providers import list_providers  # noqa: F401
