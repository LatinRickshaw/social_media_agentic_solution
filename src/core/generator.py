"""
Core generator class for social media content and image generation.
Uses GPT-4 for content and Gemini for images.
"""

from datetime import datetime
from typing import Dict, Optional, Callable, Any
import os
import time
import logging
from functools import wraps

from openai import OpenAI
import google.generativeai as genai
from PIL import Image
import io

from .config import Config, PLATFORM_SPECS
from .prompt_templates import PLATFORM_TEMPLATES, IMAGE_PROMPT_TEMPLATE

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
    using GPT-4 and Gemini respectively.
    """

    def __init__(self):
        """Initialize the generator with API connections"""
        # Validate configuration
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured")

        # Initialize OpenAI for content generation
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.temperature = Config.OPENAI_TEMPERATURE

        # Initialize Gemini for image generation
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.image_model = genai.GenerativeModel("gemini-1.5-pro")

        # Load platform specifications
        self.platform_specs = PLATFORM_SPECS
        self.templates = PLATFORM_TEMPLATES

        logger.info("SocialMediaGenerator initialized successfully")

    def generate_post(
        self,
        user_prompt: str,
        platform: str,
        context: str = "",
        brand_voice: str = "professional and engaging",
    ) -> Dict:
        """
        Generate a complete social media post for a specific platform.

        Args:
            user_prompt: The main topic/idea from the user
            platform: Target platform (linkedin, twitter, facebook, nextdoor)
            context: Additional context or requirements
            brand_voice: Desired brand voice/tone

        Returns:
            Dict containing:
                - content: Generated text content
                - image_path: Path to generated image
                - image_prompt: Prompt used for image generation
                - metadata: Platform specs, character count, etc.
        """
        if platform not in self.platform_specs:
            raise ValueError(f"Unsupported platform: {platform}")

        # 1. Generate platform-optimized content
        content = self._generate_content(user_prompt, platform, context, brand_voice)

        # 2. Extract/generate image description from content
        image_prompt = self._create_image_prompt(content, platform, user_prompt)

        # 3. Generate image with Gemini
        image_path = self._generate_image(image_prompt, platform)

        # 4. Package the result
        post_data = {
            "content": content,
            "image_path": image_path,
            "image_prompt": image_prompt,
            "platform": platform,
            "metadata": {
                "char_count": len(content),
                "char_limit": self.platform_specs[platform]["char_limit"],
                "image_size": self.platform_specs[platform]["image_size"],
                "timestamp": datetime.now().isoformat(),
            },
        }

        return post_data

    def generate_all_platforms(
        self, user_prompt: str, context: str = "", brand_voice: str = "professional and engaging"
    ) -> Dict[str, Optional[Dict]]:
        """
        Generate posts for all platforms simultaneously.

        Returns:
            Dict mapping platform name to post data
        """
        posts: Dict[str, Optional[Dict]] = {}

        for platform in self.platform_specs.keys():
            try:
                posts[platform] = self.generate_post(user_prompt, platform, context, brand_voice)
            except Exception as e:
                print(f"Error generating {platform} post: {e}")
                posts[platform] = None

        return posts

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _generate_content(
        self, user_prompt: str, platform: str, context: str, brand_voice: str
    ) -> str:
        """
        Generate platform-specific text content using GPT-4.
        Includes retry logic with exponential backoff.
        """
        # Format the prompt from template
        template = self.templates[platform]
        formatted_prompt = template.format(
            topic=user_prompt, context=context or "None", brand_voice=brand_voice
        )

        logger.info(f"Generating content for {platform}")

        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert social media content creator."},
                {"role": "user", "content": formatted_prompt},
            ],
            temperature=self.temperature,
            max_tokens=1000,
        )

        result = response.choices[0].message.content.strip()

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

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at concise social media writing."},
                {"role": "user", "content": shorten_prompt},
            ],
            temperature=self.temperature,
            max_tokens=500,
        )

        result = response.choices[0].message.content.strip()

        # If still too long, truncate with ellipsis
        if len(result) > char_limit:
            logger.warning("Content still exceeds limit after regeneration. Truncating.")
            result = result[: char_limit - 3] + "..."

        return result

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _create_image_prompt(self, content: str, platform: str, original_prompt: str) -> str:
        """
        Create an image generation prompt based on the post content.
        Uses GPT-4 to extract visual concepts.
        """
        formatted_prompt = IMAGE_PROMPT_TEMPLATE.format(
            content=content, topic=original_prompt, platform=platform
        )

        logger.info(f"Creating image prompt for {platform}")

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating visual image prompts.",
                },
                {"role": "user", "content": formatted_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        image_prompt = response.choices[0].message.content.strip()
        logger.info(f"Image prompt created: {image_prompt[:100]}...")

        return image_prompt

    @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0)
    def _generate_image(self, image_prompt: str, platform: str) -> str:
        """
        Generate image using Google Gemini Imagen 3 and save to disk.
        Returns path to saved image.
        """
        # Get platform-specific image dimensions
        width, height = self.platform_specs[platform]["image_size"]

        logger.info(f"Generating image for {platform} ({width}x{height})")

        try:
            # Generate image using Gemini's imagen-3.0-generate-001 model
            # Note: As of 2025, Gemini API supports text-to-image via generateContent
            imagen_model = genai.GenerativeModel("imagen-3.0-generate-001")

            # Enhance prompt with size requirements
            enhanced_prompt = (
                f"{image_prompt}\n\n"
                f"Image specifications: {width}x{height}px, "
                f"high quality, professional, suitable for {platform} social media."
            )

            response = imagen_model.generate_content(
                enhanced_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.4,  # Lower temperature for more consistent images
                ),
            )

            # Create output directory
            output_dir = "generated_images"
            os.makedirs(output_dir, exist_ok=True)

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(output_dir, f"{platform}_{timestamp}.png")

            # Extract and save image
            if hasattr(response, "parts") and len(response.parts) > 0:
                # Get image data from response
                image_part = response.parts[0]

                if hasattr(image_part, "inline_data"):
                    # Save the image bytes
                    image_data = image_part.inline_data.data

                    # Load with PIL to resize if needed
                    img = Image.open(io.BytesIO(image_data))

                    # Resize to exact platform dimensions
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.Resampling.LANCZOS)

                    # Save as PNG
                    img.save(image_path, "PNG", quality=95)
                    logger.info(f"Image saved to {image_path}")
                else:
                    raise ValueError("No image data in response")
            else:
                raise ValueError("Invalid response format from Imagen")

            return image_path

        except Exception as e:
            logger.error(f"Error generating image with Gemini: {e}")

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
        "--voice", "-v", default="professional and engaging", help="Desired brand voice/tone"
    )

    args = parser.parse_args()

    # Display header
    print("\n" + "=" * 70)
    print("  SOCIAL MEDIA GENERATOR - CLI")
    print("=" * 70)
    print(f"\nTopic: {args.prompt}")
    print(f"Platform(s): {args.platform}")
    print(f"Context: {args.context}")
    print(f"Brand Voice: {args.voice}")
    print("\n" + "-" * 70 + "\n")

    try:
        # Initialize generator
        generator = SocialMediaGenerator()

        # Generate posts
        if args.platform == "all":
            posts = generator.generate_all_platforms(
                args.prompt, context=args.context, brand_voice=args.voice
            )
        else:
            post = generator.generate_post(
                args.prompt, platform=args.platform, context=args.context, brand_voice=args.voice
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

                # Display metadata
                print(f"\n{'-' * 70}")
                print(f"Character limit: {post_data['metadata']['char_limit']}")
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
