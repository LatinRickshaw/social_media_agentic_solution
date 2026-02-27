"""
Tests for the __main__ CLI argument parsing in src.core.generator.

Covers:
- Default provider selection (falls back to Config.DEFAULT_*_PROVIDER)
- Valid per-element provider overrides
- Invalid provider name rejection (argparse exits with code 2)
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_parser():
    """Replicate the argparse setup from generator.__main__ for unit testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Social Media Generator - CLI Interface")

    parser.add_argument("prompt", nargs="?", default="default prompt")
    parser.add_argument(
        "--platform",
        "-p",
        choices=["linkedin", "twitter", "facebook", "nextdoor", "all"],
        default="all",
    )
    parser.add_argument("--context", "-c", default="Focus on productivity and team efficiency")
    parser.add_argument("--voice", "-v", default=None)
    parser.add_argument("--no-hashtags", action="store_true")

    _TEXT_CHOICES = ["anthropic", "openai", "gemini"]
    _IMAGE_CHOICES = ["gemini", "openai"]

    parser.add_argument("--content-provider", choices=_TEXT_CHOICES, default=None)
    parser.add_argument("--hashtag-provider", choices=_TEXT_CHOICES, default=None)
    parser.add_argument("--image-prompt-provider", choices=_TEXT_CHOICES, default=None)
    parser.add_argument("--image-provider", choices=_IMAGE_CHOICES, default=None)

    return parser


# ---------------------------------------------------------------------------
# Tests: argument defaults
# ---------------------------------------------------------------------------


class TestProviderArgDefaults:
    def test_all_provider_args_default_to_none(self):
        parser = _build_parser()
        args = parser.parse_args([])
        assert args.content_provider is None
        assert args.hashtag_provider is None
        assert args.image_prompt_provider is None
        assert args.image_provider is None

    def test_non_provider_defaults(self):
        parser = _build_parser()
        args = parser.parse_args([])
        assert args.platform == "all"
        assert args.no_hashtags is False
        assert args.voice is None


# ---------------------------------------------------------------------------
# Tests: valid provider overrides
# ---------------------------------------------------------------------------


class TestValidProviderChoices:
    @pytest.mark.parametrize("provider", ["anthropic", "openai", "gemini"])
    def test_content_provider_valid(self, provider):
        parser = _build_parser()
        args = parser.parse_args(["--content-provider", provider])
        assert args.content_provider == provider

    @pytest.mark.parametrize("provider", ["anthropic", "openai", "gemini"])
    def test_hashtag_provider_valid(self, provider):
        parser = _build_parser()
        args = parser.parse_args(["--hashtag-provider", provider])
        assert args.hashtag_provider == provider

    @pytest.mark.parametrize("provider", ["anthropic", "openai", "gemini"])
    def test_image_prompt_provider_valid(self, provider):
        parser = _build_parser()
        args = parser.parse_args(["--image-prompt-provider", provider])
        assert args.image_prompt_provider == provider

    @pytest.mark.parametrize("provider", ["gemini", "openai"])
    def test_image_provider_valid(self, provider):
        parser = _build_parser()
        args = parser.parse_args(["--image-provider", provider])
        assert args.image_provider == provider

    def test_all_providers_overridden_together(self):
        parser = _build_parser()
        args = parser.parse_args(
            [
                "--content-provider",
                "anthropic",
                "--hashtag-provider",
                "gemini",
                "--image-prompt-provider",
                "openai",
                "--image-provider",
                "openai",
            ]
        )
        assert args.content_provider == "anthropic"
        assert args.hashtag_provider == "gemini"
        assert args.image_prompt_provider == "openai"
        assert args.image_provider == "openai"


# ---------------------------------------------------------------------------
# Tests: invalid provider names rejected by argparse
# ---------------------------------------------------------------------------


class TestInvalidProviderChoices:
    def test_invalid_content_provider_exits(self):
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--content-provider", "unknown"])
        assert exc_info.value.code == 2

    def test_invalid_image_provider_exits(self):
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--image-provider", "anthropic"])  # anthropic not in image choices
        assert exc_info.value.code == 2

    def test_invalid_hashtag_provider_exits(self):
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--hashtag-provider", "badprovider"])
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# Tests: ProviderConfig is built with correct providers
# ---------------------------------------------------------------------------


class TestProviderConfigWiring:
    def _run_with_mocked_registry(self, extra_argv=None):
        """
        Run the __main__ block with registry + SocialMediaGenerator mocked so
        we can assert which providers were selected without real API calls.
        """
        argv = ["src.core.generator"] + (extra_argv or [])
        mock_text = MagicMock()
        mock_image = MagicMock()
        mock_generator_instance = MagicMock()
        mock_generator_instance.generate_all_platforms.return_value = {}

        captured_config = {}

        def fake_ssg(provider_config=None):
            captured_config["provider_config"] = provider_config
            return mock_generator_instance

        with patch("sys.argv", argv), patch(
            "src.core.providers.registry.get_text_provider", return_value=mock_text
        ) as mock_get_text, patch(
            "src.core.providers.registry.get_image_provider", return_value=mock_image
        ) as mock_get_image, patch(
            "src.core.generator.SocialMediaGenerator", side_effect=fake_ssg
        ):
            import runpy

            runpy.run_module("src.core.generator", run_name="__main__", alter_sys=False)

        return captured_config, mock_get_text, mock_get_image

    def test_defaults_use_config_providers(self):
        from src.core.config import Config

        captured, mock_get_text, mock_get_image = self._run_with_mocked_registry()

        mock_get_text.assert_any_call(Config.DEFAULT_CONTENT_PROVIDER)
        mock_get_text.assert_any_call(Config.DEFAULT_HASHTAG_PROVIDER)
        mock_get_text.assert_any_call(Config.DEFAULT_IMAGE_PROMPT_PROVIDER)
        mock_get_image.assert_any_call(Config.DEFAULT_IMAGE_PROVIDER)

    def test_cli_overrides_replace_defaults(self):
        captured, mock_get_text, mock_get_image = self._run_with_mocked_registry(
            ["--content-provider", "anthropic", "--image-provider", "openai"]
        )

        mock_get_text.assert_any_call("anthropic")
        mock_get_image.assert_any_call("openai")

    def test_image_provider_not_called_with_text_registry_fn(self):
        # Ensure image provider is fetched via get_image_provider, not get_text_provider
        from src.core.config import Config

        captured, mock_get_text, mock_get_image = self._run_with_mocked_registry()

        text_calls = [call.args[0] for call in mock_get_text.call_args_list]
        image_calls = [call.args[0] for call in mock_get_image.call_args_list]

        assert Config.DEFAULT_IMAGE_PROVIDER not in text_calls
        assert Config.DEFAULT_IMAGE_PROVIDER in image_calls
