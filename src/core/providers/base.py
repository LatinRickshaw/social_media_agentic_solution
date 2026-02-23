"""
ARCHITECTURAL DECISION: ABC over Protocol for Provider Interfaces

Context: SOC-16 requires abstract base classes for TextProvider and ImageProvider
to enable per-element AI provider selection across content, hashtags, image_prompt,
and image generation tasks.

Decision: Use abc.ABC + @abstractmethod rather than typing.Protocol.

Alternatives:
  - typing.Protocol: structural subtyping, no explicit inheritance, type-checker only
  - abc.ABC: nominal subtyping, enforced at instantiation, raises TypeError at runtime

Rationale: Ticket explicitly specifies "abstract base classes"; runtime enforcement
ensures provider implementors satisfy the contract without relying solely on static
type checkers. Explicit inheritance also makes the provider hierarchy self-documenting.

Date: 2026-02-23
Ticket: SOC-16
Author: Claude Sonnet 4.6
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


class TextProvider(ABC):
    """Abstract base class for text generation providers.

    Implementors must generate text given a system prompt, a user prompt,
    a token budget, and a sampling temperature.
    """

    @abstractmethod
    def generate_text(
        self,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text from a prompt.

        Args:
            system: System-level instructions for the model.
            prompt: User-facing prompt describing the generation task.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).

        Returns:
            Generated text as a string.
        """


class ImageProvider(ABC):
    """Abstract base class for image generation providers.

    Implementors must generate an image given a descriptive prompt and
    target dimensions, returning raw image bytes.
    """

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        width: int,
        height: int,
    ) -> bytes:
        """Generate an image from a prompt.

        Args:
            prompt: Descriptive prompt for the image to generate.
            width: Target image width in pixels.
            height: Target image height in pixels.

        Returns:
            Raw image bytes (e.g. PNG or JPEG).
        """


@dataclass
class ProviderConfig:
    """Per-element provider selection for a single generation request.

    Each field maps a generation task to a specific provider instance.
    Fields default to None, meaning the caller should fall back to a
    configured default provider when a field is not set.

    Attributes:
        content: Provider used to generate the main post content.
        hashtags: Provider used to generate hashtags.
        image_prompt: Provider used to generate the image description prompt.
        image: Provider used to generate the final image.
    """

    content: Optional[TextProvider] = field(default=None)
    hashtags: Optional[TextProvider] = field(default=None)
    image_prompt: Optional[TextProvider] = field(default=None)
    image: Optional[ImageProvider] = field(default=None)
