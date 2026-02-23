"""
Unit tests for src.core.providers.base — TextProvider, ImageProvider, ProviderConfig.
"""

import pytest
from src.core.providers.base import ImageProvider, ProviderConfig, TextProvider


# ---------------------------------------------------------------------------
# Concrete stubs used across tests
# ---------------------------------------------------------------------------


class ConcreteTextProvider(TextProvider):
    def generate_text(self, system: str, prompt: str, max_tokens: int, temperature: float) -> str:
        return f"text:{system}:{prompt}:{max_tokens}:{temperature}"


class ConcreteImageProvider(ImageProvider):
    def generate_image(self, prompt: str, width: int, height: int) -> bytes:
        return f"image:{prompt}:{width}:{height}".encode()


# ---------------------------------------------------------------------------
# TextProvider tests
# ---------------------------------------------------------------------------


class TestTextProvider:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            TextProvider()  # type: ignore[abstract]

    def test_subclass_without_generate_text_raises(self):
        class Incomplete(TextProvider):
            pass

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_concrete_implementation_instantiates(self):
        provider = ConcreteTextProvider()
        assert isinstance(provider, TextProvider)

    def test_generate_text_returns_string(self):
        provider = ConcreteTextProvider()
        result = provider.generate_text(
            system="You are helpful.",
            prompt="Write a post",
            max_tokens=100,
            temperature=0.7,
        )
        assert isinstance(result, str)

    def test_generate_text_receives_correct_arguments(self):
        provider = ConcreteTextProvider()
        result = provider.generate_text(system="sys", prompt="pmt", max_tokens=50, temperature=0.5)
        assert result == "text:sys:pmt:50:0.5"


# ---------------------------------------------------------------------------
# ImageProvider tests
# ---------------------------------------------------------------------------


class TestImageProvider:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            ImageProvider()  # type: ignore[abstract]

    def test_subclass_without_generate_image_raises(self):
        class Incomplete(ImageProvider):
            pass

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_concrete_implementation_instantiates(self):
        provider = ConcreteImageProvider()
        assert isinstance(provider, ImageProvider)

    def test_generate_image_returns_bytes(self):
        provider = ConcreteImageProvider()
        result = provider.generate_image(prompt="a sunset", width=1024, height=1024)
        assert isinstance(result, bytes)

    def test_generate_image_receives_correct_arguments(self):
        provider = ConcreteImageProvider()
        result = provider.generate_image(prompt="sunset", width=512, height=256)
        assert result == b"image:sunset:512:256"


# ---------------------------------------------------------------------------
# ProviderConfig tests
# ---------------------------------------------------------------------------


class TestProviderConfig:
    def test_default_construction_all_none(self):
        config = ProviderConfig()
        assert config.content is None
        assert config.hashtags is None
        assert config.image_prompt is None
        assert config.image is None

    def test_partial_construction_retains_nones(self):
        text = ConcreteTextProvider()
        config = ProviderConfig(content=text)
        assert config.content is text
        assert config.hashtags is None
        assert config.image_prompt is None
        assert config.image is None

    def test_full_construction(self):
        text = ConcreteTextProvider()
        img = ConcreteImageProvider()
        config = ProviderConfig(
            content=text,
            hashtags=text,
            image_prompt=text,
            image=img,
        )
        assert config.content is text
        assert config.hashtags is text
        assert config.image_prompt is text
        assert config.image is img

    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(ProviderConfig)

    def test_fields_are_independent(self):
        text1 = ConcreteTextProvider()
        text2 = ConcreteTextProvider()
        config = ProviderConfig(content=text1, hashtags=text2)
        assert config.content is not config.hashtags


# ---------------------------------------------------------------------------
# Import path tests (acceptance criteria)
# ---------------------------------------------------------------------------


class TestImportPaths:
    def test_import_from_base(self):
        from src.core.providers.base import ImageProvider  # noqa: F401
        from src.core.providers.base import ProviderConfig  # noqa: F401
        from src.core.providers.base import TextProvider  # noqa: F401

    def test_import_from_package(self):
        from src.core.providers import ImageProvider  # noqa: F401
        from src.core.providers import ProviderConfig  # noqa: F401
        from src.core.providers import TextProvider  # noqa: F401
