"""FastAPI application exposing social media generation as a REST service."""

from typing import Any, Dict, Optional

from fastapi import FastAPI

from src.core.config import Config
from src.core.generator import SocialMediaGenerator
from src.core.providers.base import ProviderConfig
from src.core.providers.registry import get_image_provider, get_text_provider, list_providers

from .models import GenerateRequest, GenerateResponse, ProviderOverrides

app = FastAPI(title="Social Media Generator API")


@app.get("/health")
def health() -> Dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}


@app.get("/providers")
def providers() -> Dict[str, Any]:
    """Return all available provider names grouped by type."""
    return list_providers()


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate social media post(s) for one or all platforms.

    Provider names in the request body are validated by Pydantic before this
    function runs; unknown names are rejected with HTTP 422 automatically.
    """
    provider_config = _build_provider_config(request.providers)
    generator = SocialMediaGenerator(provider_config=provider_config)

    if request.platform == "all":
        posts = generator.generate_all_platforms(request.prompt)
    else:
        posts = {request.platform: generator.generate_post(request.prompt, request.platform)}

    return GenerateResponse(posts=posts)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_provider_config(overrides: Optional[ProviderOverrides]) -> ProviderConfig:
    """Build a ProviderConfig, applying any per-request overrides over defaults."""
    defaults = Config.default_provider_config()

    if overrides is None:
        return defaults

    return ProviderConfig(
        content=get_text_provider(overrides.content) if overrides.content else defaults.content,
        hashtags=get_text_provider(overrides.hashtags) if overrides.hashtags else defaults.hashtags,
        image_prompt=(
            get_text_provider(overrides.image_prompt)
            if overrides.image_prompt
            else defaults.image_prompt
        ),
        image=get_image_provider(overrides.image) if overrides.image else defaults.image,
    )
