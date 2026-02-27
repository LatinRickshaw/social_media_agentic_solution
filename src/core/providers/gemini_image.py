"""
ARCHITECTURAL DECISION: generate_images() over generate_content() for Imagen 3

Context: SOC-18 extracts Gemini image generation into GeminiImageProvider.
generator.py currently calls client.models.generate_content() with Imagen 3, which
is the text/multimodal content API. The google-genai SDK separately provides
client.models.generate_images(), which is purpose-built for image generation models.

Decision: Use generate_images() with GenerateImagesConfig.

Alternatives:
1. generate_content() — current generator.py approach:
   - Response access: response.parts[0].inline_data.data
   - Designed for text/multimodal generation, not image-only models
   - Rejected: semantically incorrect API for Imagen; fragile hasattr() guards needed

2. generate_images() — chosen:
   - Response access: response.generated_images[0].image.image_bytes
   - Purpose-built for Imagen image generation models
   - Cleaner response parsing, no defensive attribute checks required

Rationale:
- generate_images() is the documented, dedicated API for Imagen models
- Produces equivalent output (raw PNG bytes) while using the correct API surface
- Ticket specifies "equivalent output", not "identical API call"

Date: 2026-02-27
Ticket: SOC-18
Author: Claude Sonnet 4.6
"""

from typing import Optional

from google import genai

from src.core.config import Config
from src.core.providers.base import ImageProvider


class GeminiImageProvider(ImageProvider):
    """ImageProvider backed by Google Gemini Imagen 3."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self._api_key = api_key if api_key is not None else Config.GOOGLE_API_KEY
        self._model = model if model is not None else Config.GEMINI_IMAGE_MODEL
        if not self._api_key:
            raise ValueError(
                "Google API key not configured. "
                "Set GOOGLE_API_KEY environment variable or pass api_key."
            )
        self._client = genai.Client(api_key=self._api_key)

    def generate_image(self, prompt: str, width: int, height: int) -> bytes:
        """Generate an image via Google Gemini Imagen 3.

        Args:
            prompt: Descriptive prompt for the image to generate.
            width: Target image width in pixels (informational; Imagen controls output size).
            height: Target image height in pixels (informational; Imagen controls output size).

        Returns:
            Raw image bytes (PNG).
        """
        response = self._client.models.generate_images(
            model=self._model,
            prompt=prompt,
            config=genai.types.GenerateImagesConfig(number_of_images=1),
        )
        return response.generated_images[0].image.image_bytes
