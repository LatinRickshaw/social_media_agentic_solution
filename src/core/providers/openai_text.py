"""
ARCHITECTURAL DECISION: Injectable Constructor with Config Fallback

Context: SOC-17 requires OpenAITextProvider to read its API key from Config
by default but remain unit-testable without live environment variables.

Decision: Accept optional api_key and model in __init__; fall back to Config
values when not supplied; raise ValueError at construction time if key absent.

Alternatives:
  - Read Config only: simpler but untestable without patching env vars globally
  - Read Config lazily at call time: defers misconfiguration discovery too late

Rationale: Fail-fast at __init__ surfaces missing credentials immediately;
injection makes test setup trivial without patching global state.

Date: 2026-02-23
Ticket: SOC-17
Author: Claude Sonnet 4.6
"""

from typing import Optional

import openai

from src.core.config import Config
from src.core.providers.base import TextProvider


class OpenAITextProvider(TextProvider):
    """TextProvider backed by the OpenAI Chat Completions API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else Config.OPENAI_API_KEY
        self._model = model if model is not None else Config.OPENAI_MODEL
        if not self._api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or pass api_key."
            )
        self._client = openai.OpenAI(api_key=self._api_key)

    def generate_text(
        self,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text via OpenAI chat completions."""
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
