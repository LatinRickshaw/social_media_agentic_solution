"""
Core generator class for social media content and image generation.

ARCHITECTURAL DECISION: ProviderConfig injection over hardcoded SDK clients

Context: SOC-20 requires SocialMediaGenerator to delegate AI calls through
the provider abstraction layer (SOC-16/17/18/19) instead of calling OpenAI
and Google Gemini SDKs directly.

Decision: Accept Optional[ProviderConfig] in __init__, defaulting to
Config.default_provider_config() when not provided.

Alternatives:
1. Required ProviderConfig argument (not Optional):
   - Pros: Explicit; callers cannot accidentally use wrong providers
   - Cons: Breaks zero-arg SocialMediaGenerator() call in streamlit_app.py
   - Rejected: Must maintain backward compatibility

2. Class-level default provider config (classvar):
   - Pros: Mutable at class level for testing
   - Cons: Shared mutable state; harder to reason about
   - Rejected: Instance-level injection is cleaner

Rationale:
- Optional param preserves backward compatibility for streamlit_app.py
- Lazy default via Config.default_provider_config() defers API key validation
  to first use, consistent with provider lazy-init pattern from SOC-19
- Consistent with existing optional param pattern (brand_guidelines_path)

Date: 2026-02-27
Ticket: SOC-20
Author: Claude Sonnet 4.6

---

ARCHITECTURAL DECISION: Migration from google-generativeai to google-genai

Context: The google-generativeai package (v0.8.0+) was officially deprecated and archived
by Google on November 30, 2025. All support, including security patches and bug fixes, has
ended. Google released the unified google-genai SDK to support Gemini 2.0 and future models.

Decision: Migrate to google-genai package (>=0.2.0) using the new client-based API.

Alternatives:
1. Continue with deprecated package - rejected due to security and support risks
2. Switch to Vertex AI SDK - rejected as it requires GCP and is more complex for our use case
3. Find alternative image generation service - rejected to maintain consistency

Rationale:
- google-genai is the official successor with active support
- Client-based architecture aligns with our existing OpenAI client pattern
- Maintains same functionality while ensuring future compatibility
- Unified SDK provides better type safety and clearer API design

Date: 2026-01-08
Ticket: SOC-14
"""

from datetime import datetime
from typing import Dict, Optional, Callable, Any
import os
import time
import logging
from functools import wraps

from PIL import Image
import io

from .config import Config, PLATFORM_SPECS
from .providers import ProviderConfig
from .providers.base import ImageProvider, TextProvider
from .prompt_templates import PLATFORM_TEMPLATES, IMAGE_PROMPT_TEMPLATE
from .brand_voice import BrandVoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed "
                            f"(attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= exponential_base
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )

            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed without exception")

        return wrapper

    return decorator


class SocialMediaGenerator:
    """
    Core generator class that orchestrates content and image generation
    via the configured provider abstraction layer.
    """

    def __init__(
        self,
        brand_guidelines_path: Optional[str] = None,
        provider_config: Optional[ProviderConfig] = None,
    ):
        """
        Initialize the generator.

        Args:
            brand_guidelines_path: Optional path to brand guidelines YAML file.
            provider_config: Provider instances to use for each generation task.
                Defaults to Config.default_provider_config() when not provided,
                which reads DEFAULT_*_PROVIDER env vars to select providers.
        """
        # Use injected config or build from env-var defaults.
        # Provider constructors validate API keys eagerly, so errors surface here.
        self._provider_config = (
            provider_config if provider_config is not None else Config.default_provider_config()
        )

        # Validate all four fields are set; store as typed attrs for mypy.
        if self._provider_config.content is None:
            raise ValueError("ProviderConfig.content must be set")
        if self._provider_config.hashtags is None:
            raise ValueError("ProviderConfig.hashtags must be set")
        if self._provider_config.image_prompt is None:
            raise ValueError("ProviderConfig.image_prompt must be set")
        if self._provider_config.image is None:
            raise ValueError("ProviderConfig.image must be set")
        self._content_provider: TextProvider = self._provider_config.content
        self._hashtag_provider: TextProvider = self._provider_config.hashtags
        self._image_prompt_provider: TextProvider = self._provider_config.image_prompt
        self._image_provider: ImageProvider = self._provider_config.image

        # Sampling temperature for text generation tasks
        self.temperature = Config.OPENAI_TEMPERATURE

        # Load platform specifications
        self.platform_specs = PLATFORM_SPECS
        self.templates = PLATFORM_TEMPLATES

        # Initialize brand voice manager
        self.brand_voice = BrandVoice(brand_guidelines_path)

        logger.info("SocialMediaGenerator initialized successfully")

    def generate_post(
        self,
        user_prompt: str,
        platform: str,
        context: str = "",
        brand_voice: Optional[str] = None,
        include_hashtags: bool = True,
    ) -> Dict:
        """
        Generate a complete social media post for a specific platform.

        Args:
            user_prompt: The main topic/idea from the user
            platform: Target platform (linkedin, twitter, facebook, nextdoor)
            context: Additional context or requirements
            brand_voice: Desired brand voice/tone (uses brand guidelines if None)
            include_hashtags: Whether to generate and include hashtags

        Returns:
            Dict containing:
                - content: Generated text content
                - hashtags: List of generated hashtags
                - image_path: Path to generated image
                - image_prompt: Prompt used for image generation
                - metadata: Platform specs, character count, brand voice used, etc.
        """
        if platform not in self.platform_specs:
            raise ValueError(f"Unsupported platform: {platform}")

        # Use brand guidelines if brand_voice not specified
        if brand_voice is None:
            brand_voice = self.brand_voice.get_brand_voice(platform)
            logger.info(f"Using brand voice from guidelines: {brand_voice}")

        # 1. Generate platform-optimized content
        content = self._generate_content(user_prompt, platform, context, brand_voice)

        # 2. Generate hashtags if requested
        hashtags = []
        if include_hashtags:
            hashtags = self._generate_hashtags(content, platform, user_prompt)
            # Append hashtags to content
            hashtag_str = self.brand_voice.format_hashtags(hashtags)
            content = f"{content}\n\n{hashtag_str}"

        # 3. Extract/generate image description from content
        image_prompt = self._create_image_prompt(content, platform, user_prompt)

        # 4. Generate image via configured image provider
        image_path = self._generate_image(image_prompt, platform)

        # 5. Package the result
        post_data = {
            "content": content,
            "hashtags": hashtags,
            "image_path": image_path,
            "image_prompt": image_prompt,
            "platform": platform,
            "metadata": {
                "char_count": len(content),
                "char_limit": self.platform_specs[platform]["char_limit"],
                "image_size": self.platform_specs[platform]["image_size"],
                "brand_voice": brand_voice,
                "timestamp": datetime.now().isoformat(),
            },
        }

        return post_data

    def generate_all_platforms(
        self,
        user_prompt: str,
        context: str = "",
        brand_voice: Optional[str] = None,
        include_hashtags: bool = True,
    ) -> Dict[str, Optional[Dict]]:
        """
        Generate posts for all platforms simultaneously.

        Args:
            user_prompt: The main topic/idea from the user
            context: Additional context or requirements
            brand_voice: Desired brand voice/tone (uses brand guidelines if None)
            include_hashtags: Whether to generate and include hashtags

        Returns:
            Dict mapping platform name to post data
        """
        posts: Dict[str, Optional[Dict]] = {}

        for platform in self.platform_specs.keys():
            try:
                posts[platform] = self.generate_post(
                    user_prompt, platform, context, brand_voice, include_hashtags
                )
            except Exception as e:
                logger.error(f"Error generating {platform} post: {e}")
                posts[platform] = None

        return posts

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _generate_content(
        self, user_prompt: str, platform: str, context: str, brand_voice: str
    ) -> str:
        """
        Generate platform-specific text content via the configured content provider.
        Includes retry logic with exponential backoff.
        """
        # Format the prompt from template
        template = self.templates[platform]
        formatted_prompt = template.format(
            topic=user_prompt, context=context or "None", brand_voice=brand_voice
        )

        logger.info(f"Generating content for {platform}")

        result = self._content_provider.generate_text(
            system="You are an expert social media content creator.",
            prompt=formatted_prompt,
            max_tokens=1000,
            temperature=self.temperature,
        ).strip()

        # Validate and adjust character count
        char_limit = self.platform_specs[platform]["char_limit"]
        if len(result) > char_limit:
            logger.warning(
                f"Content exceeds {platform} limit ({len(result)} > {char_limit}). "
                f"Requesting regeneration..."
            )
            # Request a shorter version
            result = self._regenerate_shorter_content(
                result, platform, char_limit, user_prompt, context, brand_voice
            )

        logger.info(f"Generated {len(result)} characters for {platform}")
        return result

    def _regenerate_shorter_content(
        self,
        original_content: str,
        platform: str,
        char_limit: int,
        user_prompt: str,
        context: str,
        brand_voice: str,
    ) -> str:
        """
        Regenerate content to fit within character limit.
        """
        shorten_prompt = f"""
The following content is too long for {platform} (limit: {char_limit} characters).

Original content:
{original_content}

Please rewrite this to be under {char_limit} characters while maintaining the key message,
tone ({brand_voice}), and call-to-action. Keep it engaging and complete.
"""

        result = self._content_provider.generate_text(
            system="You are an expert at concise social media writing.",
            prompt=shorten_prompt,
            max_tokens=500,
            temperature=self.temperature,
        ).strip()

        # If still too long, truncate with ellipsis
        if len(result) > char_limit:
            logger.warning("Content still exceeds limit after regeneration. Truncating.")
            result = result[: char_limit - 3] + "..."

        return result

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _create_image_prompt(self, content: str, platform: str, original_prompt: str) -> str:
        """
        Create an image generation prompt based on the post content.
        Uses the configured image-prompt provider to extract visual concepts.
        """
        formatted_prompt = IMAGE_PROMPT_TEMPLATE.format(
            content=content, topic=original_prompt, platform=platform
        )

        logger.info(f"Creating image prompt for {platform}")

        image_prompt = self._image_prompt_provider.generate_text(
            system="You are an expert at creating visual image prompts.",
            prompt=formatted_prompt,
            max_tokens=300,
            temperature=0.7,
        ).strip()
        logger.info(f"Image prompt created: {image_prompt[:100]}...")

        return image_prompt

    @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)
    def _generate_image(self, image_prompt: str, platform: str) -> str:
        """
        Generate image via the configured image provider and save to disk.
        Returns path to saved image.
        """
        # Get platform-specific image dimensions
        width, height = self.platform_specs[platform]["image_size"]

        logger.info(f"Generating image for {platform} ({width}x{height})")

        try:
            # Enhance prompt with size requirements
            enhanced_prompt = (
                f"{image_prompt}\n\n"
                f"Image specifications: {width}x{height}px, "
                f"high quality, professional, suitable for {platform} social media."
            )

            # Delegate to the configured image provider — returns raw PNG bytes
            image_data = self._image_provider.generate_image(
                prompt=enhanced_prompt,
                width=width,
                height=height,
            )

            # Create output directory
            output_dir = "generated_images"
            os.makedirs(output_dir, exist_ok=True)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(output_dir, f"{platform}_{timestamp}.png")

            # Load with PIL to resize if needed, then save
            img = Image.open(io.BytesIO(image_data))
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(image_path, "PNG", quality=95)
            logger.info(f"Image saved to {image_path}")

            return image_path

        except Exception as e:
            logger.error(f"Error generating image: {e}")

            # Create a simple placeholder image instead of failing
            image_path = self._create_placeholder_image(platform, image_prompt)
            logger.warning(f"Created placeholder image at {image_path}")

            return image_path

    def _create_placeholder_image(self, platform: str, prompt: str) -> str:
        """
        Create a placeholder image when generation fails.
        """
        width, height = self.platform_specs[platform]["image_size"]

        # Create a simple colored image with text
        img = Image.new("RGB", (width, height), color=(240, 240, 245))

        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(output_dir, f"{platform}_{timestamp}_placeholder.png")

        img.save(image_path, "PNG")

        # Also save the prompt to a text file
        text_path = image_path.replace(".png", "_prompt.txt")
        with open(text_path, "w") as f:
            f.write(f"Platform: {platform}\n")
            f.write(f"Dimensions: {width}x{height}\n")
            f.write(f"Prompt: {prompt}\n")

        return image_path

    def regenerate_image(self, content: str, platform: str, original_prompt: str) -> Dict:
        """
        Regenerate just the image for existing content.

        Returns:
            Dict with new image_path and image_prompt
        """
        image_prompt = self._create_image_prompt(content, platform, original_prompt)
        image_path = self._generate_image(image_prompt, platform)

        return {"image_path": image_path, "image_prompt": image_prompt}

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _generate_hashtags(self, content: str, platform: str, topic: str) -> list:
        """
        Generate relevant hashtags for the post via the configured hashtag provider.

        Args:
            content: The generated post content
            platform: Target platform
            topic: Original topic/prompt

        Returns:
            List of hashtag strings (without # symbol)
        """
        # Get platform-specific hashtag count
        max_hashtags = self.platform_specs[platform]["max_hashtags"]

        # Get hashtag strategy from brand guidelines
        strategy = self.brand_voice.get_hashtag_strategy()
        preferred_categories = strategy.get("preferred_categories", [])
        avoid_categories = strategy.get("avoid", [])

        hashtag_prompt = f"""
Generate {max_hashtags} highly relevant and effective hashtags for this {platform} post.

Post content:
{content}

Original topic: {topic}

Requirements:
- Generate EXACTLY {max_hashtags} hashtags
- Make them relevant to the content and {platform} audience
- Preferred categories: {', '.join(preferred_categories)}
- Avoid: {', '.join(avoid_categories)}
- Mix of specific and broader hashtags
- Use proper capitalization (e.g., #SocialMedia not #socialmedia)
- No spaces in hashtags
- Make them searchable and trending-friendly

Return ONLY the hashtags as a comma-separated list, without the # symbol.
Example format: Innovation, TechTrends, BusinessGrowth
"""

        logger.info(f"Generating {max_hashtags} hashtags for {platform}")

        result = self._hashtag_provider.generate_text(
            system="You are an expert at social media hashtag strategy.",
            prompt=hashtag_prompt,
            max_tokens=150,
            temperature=0.7,
        ).strip()

        # Parse the comma-separated hashtags
        hashtags = [tag.strip().replace("#", "") for tag in result.split(",")]

        # Ensure we have the right number
        hashtags = hashtags[:max_hashtags]

        logger.info(f"Generated hashtags: {hashtags}")

        return hashtags


# CLI Testing Interface
if __name__ == "__main__":
    import sys
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Social Media Generator - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for all platforms
  python -m src.core.generator "New AI feature announcement"

  # Generate for specific platform
  python -m src.core.generator "Product launch" --platform linkedin

  # With custom context and brand voice
  python -m src.core.generator "Team update" \\
    --context "Focus on collaboration" \\
    --voice "friendly and professional"
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        default="Announcing our new AI-powered feature that helps teams collaborate better",
        help="The main topic/idea for the social media post",
    )

    parser.add_argument(
        "--platform",
        "-p",
        choices=["linkedin", "twitter", "facebook", "nextdoor", "all"],
        default="all",
        help="Target platform (default: all)",
    )

    parser.add_argument(
        "--context",
        "-c",
        default="Focus on productivity and team efficiency",
        help="Additional context or requirements",
    )

    parser.add_argument(
        "--voice",
        "-v",
        default=None,
        help="Desired brand voice/tone (uses brand guidelines if not specified)",
    )

    parser.add_argument(
        "--no-hashtags",
        action="store_true",
        help="Disable hashtag generation",
    )

    args = parser.parse_args()

    # Display header
    print("\n" + "=" * 70)
    print("  SOCIAL MEDIA GENERATOR - CLI")
    print("=" * 70)
    print(f"\nTopic: {args.prompt}")
    print(f"Platform(s): {args.platform}")
    print(f"Context: {args.context}")
    print(f"Brand Voice: {args.voice or 'From brand guidelines'}")
    print(f"Hashtags: {'Disabled' if args.no_hashtags else 'Enabled'}")
    print("\n" + "-" * 70 + "\n")

    try:
        # Initialize generator
        generator = SocialMediaGenerator()

        # Generate posts
        if args.platform == "all":
            posts = generator.generate_all_platforms(
                args.prompt,
                context=args.context,
                brand_voice=args.voice,
                include_hashtags=not args.no_hashtags,
            )
        else:
            post = generator.generate_post(
                args.prompt,
                platform=args.platform,
                context=args.context,
                brand_voice=args.voice,
                include_hashtags=not args.no_hashtags,
            )
            posts = {args.platform: post}

        # Display results
        success_count = 0
        for platform, post_data in posts.items():
            print("\n" + "=" * 70)
            print(f"  {platform.upper()}")
            print(f"{'=' * 70}")

            if post_data:
                success_count += 1

                # Display content
                print(f"\nContent ({len(post_data['content'])} characters):")
                print("-" * 70)
                print(post_data["content"])

                # Display hashtags
                if post_data.get("hashtags"):
                    print(f"\n{'-' * 70}")
                    print(f"Hashtags: {', '.join(['#' + tag for tag in post_data['hashtags']])}")

                # Display metadata
                print(f"\n{'-' * 70}")
                print(f"Character limit: {post_data['metadata']['char_limit']}")
                print(f"Brand voice: {post_data['metadata']['brand_voice']}")
                print(f"Image: {post_data['image_path']}")
                print(f"Image prompt: {post_data['image_prompt'][:80]}...")
                print(f"Generated at: {post_data['metadata']['timestamp']}")
            else:
                print("\n[FAILED]")

        # Summary
        print("\n" + "=" * 70)
        print("  SUMMARY")
        print("=" * 70)
        print(f"Successfully generated: {success_count}/{len(posts)} platforms")
        print("=" * 70 + "\n")

    except ValueError as e:
        print(f"\nERROR: {e}")
        print("Please check your .env file and ensure API keys are configured.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
