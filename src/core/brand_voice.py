"""
Brand voice utilities for loading and applying brand guidelines.
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
import logging

from .config import PLATFORM_SPECS

# Configure logging
logger = logging.getLogger(__name__)


class BrandVoice:
    """Manages brand voice and guidelines"""

    def __init__(self, guidelines_path: Optional[str] = None):
        """
        Initialize brand voice manager.

        Args:
            guidelines_path: Path to brand guidelines YAML file
        """
        if guidelines_path is None:
            # Default to config/brand_guidelines.yaml
            project_root = Path(__file__).parent.parent.parent
            guidelines_path_obj: Path = project_root / "config" / "brand_guidelines.yaml"
        else:
            guidelines_path_obj = Path(guidelines_path)

        self.guidelines_path = guidelines_path_obj
        self.guidelines = self._load_guidelines()

    def _load_guidelines(self) -> Dict:
        """Load brand guidelines from YAML file"""
        if not self.guidelines_path.exists():
            raise FileNotFoundError(f"Brand guidelines not found at {self.guidelines_path}")

        try:
            with open(self.guidelines_path, "r") as f:
                guidelines = yaml.safe_load(f)

            if not isinstance(guidelines, dict):
                raise ValueError(
                    f"Brand guidelines must be a YAML dictionary, got {type(guidelines)}"
                )

            logger.info(f"Successfully loaded brand guidelines from {self.guidelines_path}")
            return guidelines

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in brand guidelines file: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to load brand guidelines: {e}") from e

    def get_brand_voice(self, platform: Optional[str] = None) -> str:
        """
        Get the brand voice description for a platform.

        Args:
            platform: Optional platform name for platform-specific voice

        Returns:
            Brand voice description string
        """
        # Get primary brand voice
        primary = self.guidelines.get("brand_voice", {}).get("primary", "professional and engaging")

        # Get tone keywords
        tone_keywords = self.guidelines.get("brand_voice", {}).get("tone_keywords", [])
        keywords_str = ", ".join(tone_keywords) if tone_keywords else ""

        # Get platform-specific preferences if available
        platform_prefs = ""
        if platform:
            prefs = self.guidelines.get("platform_preferences", {}).get(platform, {})
            if prefs:
                focus = prefs.get("focus", "")
                style = prefs.get("style", "")
                platform_prefs = f" For {platform}: {style}, focusing on {focus}."

        # Combine into comprehensive voice description
        voice = f"{primary}"
        if keywords_str:
            voice += f", emphasizing {keywords_str}"
        if platform_prefs:
            voice += platform_prefs

        return voice

    def get_hashtag_strategy(self) -> Dict:
        """Get hashtag strategy from guidelines"""
        return self.guidelines.get("hashtag_strategy", {})

    def get_cta_preferences(self) -> Dict:
        """Get call-to-action preferences"""
        return self.guidelines.get("call_to_action", {})

    def get_values(self) -> list:
        """Get brand values"""
        return self.guidelines.get("values", [])

    def get_avoidances(self) -> Dict:
        """Get things to avoid"""
        return self.guidelines.get("avoid", {})

    def get_platform_focus(self, platform: str) -> str:
        """
        Get the content focus for a specific platform.

        Args:
            platform: Platform name

        Returns:
            Focus description string
        """
        prefs = self.guidelines.get("platform_preferences", {}).get(platform, {})
        return prefs.get("focus", "")

    def get_platform_style(self, platform: str) -> str:
        """
        Get the writing style for a specific platform.

        Args:
            platform: Platform name

        Returns:
            Style description string
        """
        prefs = self.guidelines.get("platform_preferences", {}).get(platform, {})
        return prefs.get("style", "")

    def generate_hashtags(self, platform: str, topic: str, count: Optional[int] = None) -> list:
        """
        Generate appropriate hashtags based on platform and topic.

        NOTE: This is a fallback/simple implementation. For production use,
        prefer the _generate_hashtags() method in the generator which uses GPT-4.

        Args:
            platform: Target platform
            topic: Post topic/theme
            count: Number of hashtags (defaults to platform optimal)

        Returns:
            List of hashtag strings (without # symbol)
        """
        if platform not in PLATFORM_SPECS:
            max_hashtags = 3  # Default fallback
        else:
            max_hashtags = PLATFORM_SPECS[platform]["max_hashtags"]

        if count is None:
            count = max_hashtags

        # Get hashtag strategy
        strategy = self.get_hashtag_strategy()
        preferred = strategy.get("preferred_categories", [])

        # Generate basic hashtags based on topic
        # This is a simple implementation - in production, you might use
        # an LLM or hashtag API to generate optimal hashtags
        topic_words = topic.lower().replace("-", " ").split()

        # Create hashtags from topic words
        hashtags = []

        # Add topic-based hashtags
        for word in topic_words:
            if len(word) > 3 and word not in ["the", "and", "for", "with"]:
                # Capitalize first letter
                hashtag = word.capitalize()
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

        # Add some generic industry hashtags based on preferred categories
        if "industry-specific" in preferred:
            industry_tags = ["Innovation", "Technology", "Business", "Growth"]
            hashtags.extend([tag for tag in industry_tags if tag not in hashtags])

        # Limit to requested count
        return hashtags[:count]

    def format_hashtags(self, hashtags: list) -> str:
        """
        Format hashtags for inclusion in post.

        Args:
            hashtags: List of hashtag strings (with or without #)

        Returns:
            Formatted hashtag string
        """
        # Strip # if present, then add it
        return " ".join([f"#{tag.lstrip('#')}" for tag in hashtags])

    def __repr__(self):
        return f"BrandVoice(guidelines_path={self.guidelines_path})"
