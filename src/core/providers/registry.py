"""
ARCHITECTURAL DECISION: Module-level functions with lazy caching

Context: SOC-19 requires a registry that maps provider name strings to provider
instances, caches them on first use, and allows import without instantiation.
All five provider constructors validate API keys eagerly in __init__ and raise
ValueError on missing keys, so instantiation must be deferred to get_* call time.

Decision: Module-level functions with module-level cache dicts.

Alternatives:
1. Class-based registry (ProviderRegistry singleton or class with classmethods):
   - Pros: Injectable; a fresh instance per test avoids cache persistence
   - Cons: Over-engineered — ticket specifies bare function signatures, not class
     methods; adds indirection with no benefit for the stated use case.
   - Rejected: YAGNI — no use case for multiple registry instances.

2. Module-level singleton object (__call__ or __getattr__ magic):
   - Similar complexity to class approach with worse readability.
   - Rejected: unnecessary indirection.

Rationale:
- Module-level functions match the ticket's exact API surface verbatim.
- Python's module import system guarantees the dicts are initialised once.
- Cache isolation in tests is achieved via unittest.mock.patch.dict — no extra
  production surface (e.g. a reset method) required.

Date: 2026-02-27
Ticket: SOC-19
Author: Claude Sonnet 4.6
"""

from typing import Dict, List, Type

from src.core.providers.anthropic import AnthropicTextProvider
from src.core.providers.base import ImageProvider, TextProvider
from src.core.providers.gemini_image import GeminiImageProvider
from src.core.providers.gemini_text import GeminiTextProvider
from src.core.providers.openai_image import OpenAIImageProvider
from src.core.providers.openai_text import OpenAITextProvider

# ---------------------------------------------------------------------------
# Provider maps — name → class (imported at module load; no instances created)
# ---------------------------------------------------------------------------

_TEXT_PROVIDERS: Dict[str, Type[TextProvider]] = {
    "anthropic": AnthropicTextProvider,
    "openai": OpenAITextProvider,
    "gemini": GeminiTextProvider,
}

_IMAGE_PROVIDERS: Dict[str, Type[ImageProvider]] = {
    "gemini": GeminiImageProvider,
    "openai": OpenAIImageProvider,
}

# ---------------------------------------------------------------------------
# Instance caches — populated lazily on first get_* call
# ---------------------------------------------------------------------------

_text_cache: Dict[str, TextProvider] = {}
_image_cache: Dict[str, ImageProvider] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_text_provider(name: str) -> TextProvider:
    """Return a cached TextProvider instance for the given provider name.

    The provider is instantiated on the first call for each name and cached
    for all subsequent calls.  No providers are instantiated at import time.

    Args:
        name: Provider name — one of ``"anthropic"``, ``"openai"``, ``"gemini"``.

    Returns:
        Cached :class:`TextProvider` instance.

    Raises:
        ValueError: If *name* is not a known text provider, with a message
            listing all valid options.
    """
    if name not in _TEXT_PROVIDERS:
        valid = list(_TEXT_PROVIDERS)
        raise ValueError(f"Unknown text provider '{name}'. Valid options: {valid}")
    if name not in _text_cache:
        _text_cache[name] = _TEXT_PROVIDERS[name]()
    return _text_cache[name]


def get_image_provider(name: str) -> ImageProvider:
    """Return a cached ImageProvider instance for the given provider name.

    The provider is instantiated on the first call for each name and cached
    for all subsequent calls.  No providers are instantiated at import time.

    Args:
        name: Provider name — one of ``"gemini"``, ``"openai"``.

    Returns:
        Cached :class:`ImageProvider` instance.

    Raises:
        ValueError: If *name* is not a known image provider, with a message
            listing all valid options.
    """
    if name not in _IMAGE_PROVIDERS:
        valid = list(_IMAGE_PROVIDERS)
        raise ValueError(f"Unknown image provider '{name}'. Valid options: {valid}")
    if name not in _image_cache:
        _image_cache[name] = _IMAGE_PROVIDERS[name]()
    return _image_cache[name]


def list_providers() -> Dict[str, List[str]]:
    """Return all available provider names grouped by type.

    Returns:
        A dict with keys ``"text"`` and ``"image"``, each mapping to a list
        of provider name strings in registration order.  Example::

            {"text": ["anthropic", "openai", "gemini"],
             "image": ["gemini", "openai"]}
    """
    return {
        "text": list(_TEXT_PROVIDERS),
        "image": list(_IMAGE_PROVIDERS),
    }
