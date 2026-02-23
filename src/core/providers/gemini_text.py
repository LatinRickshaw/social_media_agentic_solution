"""
ARCHITECTURAL DECISION: Injectable Constructor with Config Fallback

Context: SOC-17 requires GeminiTextProvider to read its API key from Config
by default but remain unit-testable without live environment variables.

Decision: Accept optional api_key and model in __init__; fall back to Config
values when not supplied; raise ValueError at construction time if key absent.

Rationale: Same fail-fast + testability rationale as other SOC-17 providers.
GenerateContentConfig carries the system instruction, temperature, and token
budget; response.text extracts the generated string from the Gemini response.

Date: 2026-02-23
Ticket: SOC-17
Author: Claude Sonnet 4.6
"""

from typing import Optional

from google import genai

from src.core.config import Config
from src.core.providers.base import TextProvider


class GeminiTextProvider(TextProvider):
    """TextProvider backed by the Google GenAI (Gemini) API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else Config.GOOGLE_API_KEY
        self._model = model if model is not None else Config.GEMINI_TEXT_MODEL
        if not self._api_key:
            raise ValueError(
                "Google API key not configured. "
                "Set GOOGLE_API_KEY environment variable or pass api_key."
            )
        self._client = genai.Client(api_key=self._api_key)

    def generate_text(
        self,
        system: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate text via Google GenAI (Gemini) models."""
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
