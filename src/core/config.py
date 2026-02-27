"""
Configuration module for the social media generator.
Handles environment variables and platform specifications.
"""

import os
from typing import TYPE_CHECKING, Dict, Tuple, TypedDict
from dotenv import load_dotenv

if TYPE_CHECKING:
    from src.core.providers.base import ProviderConfig

# Load environment variables
load_dotenv()


class PlatformSpec(TypedDict):
    """Type definition for platform specifications"""

    char_limit: int
    optimal_length: str
    image_size: Tuple[int, int]
    image_format: str
    max_hashtags: int
    tone: str
    api_rate_limit: str


# Platform Specifications
PLATFORM_SPECS: Dict[str, PlatformSpec] = {
    "linkedin": {
        "char_limit": 3000,
        "optimal_length": "150-300 words",
        "image_size": (1200, 627),  # 1.91:1 ratio
        "image_format": "PNG/JPG",
        "max_hashtags": 5,
        "tone": "Professional, insightful",
        "api_rate_limit": "100 posts/day per person",
    },
    "twitter": {
        "char_limit": 280,
        "optimal_length": "200-270 characters",
        "image_size": (1200, 675),  # 16:9 ratio
        "image_format": "PNG/JPG/GIF",
        "max_hashtags": 2,
        "tone": "Conversational, punchy",
        "api_rate_limit": "300 posts/3 hours",
    },
    "facebook": {
        "char_limit": 63206,
        "optimal_length": "100-200 words",
        "image_size": (1200, 630),  # 1.91:1 ratio
        "image_format": "PNG/JPG",
        "max_hashtags": 5,
        "tone": "Friendly, engaging",
        "api_rate_limit": "Varies by page",
    },
    "nextdoor": {
        "char_limit": 5000,
        "optimal_length": "100-250 words",
        "image_size": (1200, 900),  # 4:3 ratio
        "image_format": "JPG/PNG",
        "max_hashtags": 3,
        "tone": "Neighborly, helpful",
        "api_rate_limit": "Limited/no public API",
    },
}


# API Configuration
class Config:
    """Application configuration"""

    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Google Gemini
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash")
    GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")

    # OpenAI Image
    OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")

    # Provider selection defaults — which provider handles each generation task
    DEFAULT_CONTENT_PROVIDER = os.getenv("DEFAULT_CONTENT_PROVIDER", "openai")
    DEFAULT_HASHTAG_PROVIDER = os.getenv("DEFAULT_HASHTAG_PROVIDER", "openai")
    DEFAULT_IMAGE_PROMPT_PROVIDER = os.getenv("DEFAULT_IMAGE_PROMPT_PROVIDER", "openai")
    DEFAULT_IMAGE_PROVIDER = os.getenv("DEFAULT_IMAGE_PROVIDER", "gemini")

    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "social_media_gen")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # LinkedIn
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

    # Facebook
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

    # Twitter/X
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

    # Storage
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "social-media-images")

    # Application
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Jira Integration
    JIRA_CLOUD_ID = os.getenv("JIRA_CLOUD_ID", "f697d2b7-9442-444e-b462-e3a9b835734f")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "SOC")

    @classmethod
    def default_provider_config(cls) -> "ProviderConfig":
        """Build a ProviderConfig from the configured DEFAULT_*_PROVIDER env vars.

        Lazy imports avoid circular dependencies (registry imports Config).
        The registry caches instances, so repeated calls are inexpensive.
        """
        from src.core.providers.base import ProviderConfig
        from src.core.providers.registry import get_image_provider, get_text_provider

        return ProviderConfig(
            content=get_text_provider(cls.DEFAULT_CONTENT_PROVIDER),
            hashtags=get_text_provider(cls.DEFAULT_HASHTAG_PROVIDER),
            image_prompt=get_text_provider(cls.DEFAULT_IMAGE_PROMPT_PROVIDER),
            image=get_image_provider(cls.DEFAULT_IMAGE_PROVIDER),
        )

    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """Validate required configuration.

        Checks only the API keys needed by the configured default providers,
        so users only need credentials for providers they actually use.
        """
        _provider_key_map = {
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "gemini": cls.GOOGLE_API_KEY,
        }
        text_providers = {
            cls.DEFAULT_CONTENT_PROVIDER,
            cls.DEFAULT_HASHTAG_PROVIDER,
            cls.DEFAULT_IMAGE_PROMPT_PROVIDER,
        }
        return {
            "text_providers": all(bool(_provider_key_map.get(p)) for p in text_providers),
            "image_provider": bool(_provider_key_map.get(cls.DEFAULT_IMAGE_PROVIDER)),
            "database": bool(cls.DB_PASSWORD),
        }

    @classmethod
    def get_platform_spec(cls, platform: str) -> PlatformSpec:
        """Get specifications for a specific platform"""
        if platform not in PLATFORM_SPECS:
            raise ValueError(f"Unsupported platform: {platform}")
        return PLATFORM_SPECS[platform]
