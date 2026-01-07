"""
Configuration module for the social media generator.
Handles environment variables and platform specifications.
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Platform Specifications
PLATFORM_SPECS = {
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

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # Google Gemini
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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
    def validate(cls) -> Dict[str, bool]:
        """Validate required configuration"""
        validations = {
            "openai": bool(cls.OPENAI_API_KEY),
            "google": bool(cls.GOOGLE_API_KEY),
            "database": bool(cls.DB_PASSWORD),
        }
        return validations

    @classmethod
    def get_platform_spec(cls, platform: str) -> Dict:
        """Get specifications for a specific platform"""
        return PLATFORM_SPECS.get(platform, {})
