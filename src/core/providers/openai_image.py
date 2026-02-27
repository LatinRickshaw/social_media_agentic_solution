"""
ARCHITECTURAL DECISION: URL download over base64 for DALL-E 3 response

Context: SOC-18 requires OpenAIImageProvider to call DALL-E 3 and return raw bytes.
The OpenAI images API supports two response formats: "url" (returns a temporary URL)
and "b64_json" (returns base64-encoded image data directly).

Decision: Use response_format="url" and download via requests.get().

Alternatives:
1. response_format="b64_json":
   - Access: base64.b64decode(response.data[0].b64_json)
   - No extra network round-trip; simpler data path
   - Rejected: ticket explicitly specifies "downloads from URL, returns bytes"

2. response_format="url" + requests.get() — chosen:
   - Access: requests.get(response.data[0].url).content
   - Matches ticket acceptance criteria exactly
   - URL is temporary (~1 hour), acceptable for immediate download

DALL-E 3 size mapping: Only three sizes are supported — "1024x1024", "1024x1792",
"1792x1024". width/height are mapped to the nearest by aspect ratio:
  landscape (width > height) → "1792x1024"
  portrait  (height > width) → "1024x1792"
  square / equal             → "1024x1024"

Date: 2026-02-27
Ticket: SOC-18
Author: Claude Sonnet 4.6
"""

from typing import Optional

import openai
import requests

from src.core.config import Config
from src.core.providers.base import ImageProvider


class OpenAIImageProvider(ImageProvider):
    """ImageProvider backed by OpenAI DALL-E 3."""

    _LANDSCAPE = "1792x1024"
    _PORTRAIT = "1024x1792"
    _SQUARE = "1024x1024"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else Config.OPENAI_API_KEY
        self._model = model if model is not None else Config.OPENAI_IMAGE_MODEL
        if not self._api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or pass api_key."
            )
        self._client = openai.OpenAI(api_key=self._api_key)

    def generate_image(self, prompt: str, width: int, height: int) -> bytes:
        """Generate an image via OpenAI DALL-E 3, downloading from the returned URL.

        Maps width/height to the nearest DALL-E 3 supported size, calls
        client.images.generate(), then downloads from the response URL.

        Args:
            prompt: Descriptive prompt for the image to generate.
            width: Target image width in pixels (used to select DALL-E 3 size variant).
            height: Target image height in pixels (used to select DALL-E 3 size variant).

        Returns:
            Raw image bytes (PNG/JPEG as returned by DALL-E 3).
        """
        size = self._derive_size(width, height)
        response = self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size=size,
            response_format="url",
            n=1,
        )
        url = response.data[0].url
        return requests.get(url, timeout=30).content

    def _derive_size(self, width: int, height: int) -> str:
        """Map arbitrary dimensions to the nearest DALL-E 3 supported size string."""
        if width > height:
            return self._LANDSCAPE
        if height > width:
            return self._PORTRAIT
        return self._SQUARE
