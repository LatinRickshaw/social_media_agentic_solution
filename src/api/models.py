"""
ARCHITECTURAL DECISION: Pydantic Literal types for provider name validation

Context: SOC-22 requires invalid provider names to return HTTP 422. Provider
names are a closed set defined by the registry (_TEXT_PROVIDERS / _IMAGE_PROVIDERS).

Decision: Use Literal type aliases for provider name fields in ProviderOverrides.
Pydantic automatically rejects values outside the Literal set with a 422
ValidationError before any endpoint logic runs.

Alternatives:
1. @field_validator that calls list_providers() at runtime:
   - Pros: Dynamic — picks up new providers without model change
   - Cons: Couples model to registry at validation time; adds indirection; the
     set of valid providers is intentionally stable (adding a provider is a
     deliberate release decision, not a runtime concern).
   - Rejected: YAGNI — the Literal approach is simpler and the provider set
     is defined at import time anyway.

2. Catch ValueError from registry in the endpoint, raise HTTPException(422):
   - Pros: Keeps validation in business logic
   - Cons: Invalid names reach endpoint logic before rejection; error messages
     are less structured than Pydantic's built-in validation errors.
   - Rejected: Pydantic validation at deserialization time is earlier and cleaner.

Rationale:
- Literal types co-locate the valid values with the model that uses them.
- Pydantic's 422 response includes a clear per-field error message automatically.
- Consistent with FastAPI idiom; no custom exception handlers required.

Date: 2026-03-03
Ticket: SOC-22
Author: Claude Sonnet 4.6
"""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Provider name type aliases — mirrors the registry's closed sets
# ---------------------------------------------------------------------------

TextProviderName = Literal["anthropic", "openai", "gemini"]
ImageProviderName = Literal["gemini", "openai"]

PlatformName = Literal["linkedin", "twitter", "facebook", "nextdoor", "all"]


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ProviderOverrides(BaseModel):
    """Per-element provider selection for a single generation request.

    All fields are optional; unset fields fall back to the server's configured
    DEFAULT_*_PROVIDER environment variables.
    """

    content: Optional[TextProviderName] = None
    hashtags: Optional[TextProviderName] = None
    image_prompt: Optional[TextProviderName] = None
    image: Optional[ImageProviderName] = None


class GenerateRequest(BaseModel):
    """Request body for POST /generate."""

    prompt: str
    platform: PlatformName
    providers: Optional[ProviderOverrides] = None


class GenerateResponse(BaseModel):
    """
    ARCHITECTURAL DECISION: Uniform keyed-by-platform response shape

    Context: generate_post() returns a single Dict; generate_all_platforms()
    returns Dict[str, Optional[Dict]]. The API needs a consistent response shape
    regardless of whether the caller requested one platform or all four.

    Decision: GenerateResponse always wraps results as posts: Dict[str, Any],
    keyed by platform name. A single-platform request returns {"linkedin": {...}};
    "all" returns {"linkedin": {...}, "twitter": {...}, ...}.

    Alternative: Return PostResult directly for single platform, Dict for "all"
    (discriminated union / overloaded response).
    Rejected: Inconsistent shape breaks client code when platform parameter
    changes; harder to type and document; adds unnecessary complexity.

    Rationale: Uniform shape means clients always iterate posts.items() — no
    branching on request parameters needed.

    Date: 2026-03-03
    Ticket: SOC-22
    Author: Claude Sonnet 4.6
    """

    posts: Dict[str, Any]
