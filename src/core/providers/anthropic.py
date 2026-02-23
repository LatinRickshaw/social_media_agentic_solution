"""
ARCHITECTURAL DECISION: Injectable Constructor with Config Fallback

Context: SOC-17 requires AnthropicTextProvider to read its API key from Config
by default but remain unit-testable without live environment variables.

Decision: Accept optional api_key and model in __init__; fall back to Config
values when not supplied; raise ValueError at construction time if key absent.

Rationale: Same fail-fast + testability rationale as other SOC-17 providers.
The Anthropic Messages API takes system as a top-level parameter (not inside
the messages list), which differs from OpenAI's convention.

Date: 2026-02-23
Ticket: SOC-17
Author: Claude Sonnet 4.6
"""

from typing import Optional

import anthropic

from src.core.config import Config
from src.core.providers.base import TextProvider


class AnthropicTextProvider(TextProvider):
    """TextProvider backed by the Anthropic Messages API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else Config.ANTHROPIC_API_KEY
        self._model = model if model is not None else Config.ANTHROPIC_MODEL
        if not self._api_key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key."
            )
        self._client = anthropic.Anthropic(api_key=self._api_key)

    def generate_text(
        self,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text via Anthropic Messages API."""
        response = self._client.messages.create(
            model=self._model,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.content[0].text
