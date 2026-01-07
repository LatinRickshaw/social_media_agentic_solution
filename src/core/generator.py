"""
Core generator class for social media content and image generation.
Uses GPT-4 for content and Gemini for images.
"""

from datetime import datetime
from typing import Dict, Optional
import os

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai

from .config import Config, PLATFORM_SPECS
from .prompt_templates import PLATFORM_TEMPLATES, IMAGE_PROMPT_TEMPLATE


class SocialMediaGenerator:
    """
    Core generator class that orchestrates content and image generation
    using GPT-4 and Gemini respectively.
    """

    def __init__(self):
        """Initialize the generator with API connections"""
        # Initialize OpenAI for content
        self.content_generator = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY,
        )

        # Initialize Gemini for images
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.image_generator = genai.GenerativeModel("gemini-pro-vision")

        # Load platform specifications
        self.platform_specs = PLATFORM_SPECS
        self.templates = PLATFORM_TEMPLATES

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

    def _generate_content(
        self, user_prompt: str, platform: str, context: str, brand_voice: str
    ) -> str:
        """
        Generate platform-specific text content using GPT-4.
        """
        # Create the prompt from template
        template = self.templates[platform]
        prompt = ChatPromptTemplate.from_template(template)

        # Create chain
        chain = LLMChain(llm=self.content_generator, prompt=prompt)

        # Generate content
        result = chain.run(topic=user_prompt, context=context, brand_voice=brand_voice)

        # Validate character count
        char_limit = self.platform_specs[platform]["char_limit"]
        if len(result) > char_limit:
            # Truncate and add ellipsis
            result = result[: char_limit - 3] + "..."

        return result.strip()

    def _create_image_prompt(self, content: str, platform: str, original_prompt: str) -> str:
        """
        Create an image generation prompt based on the post content.
        Uses GPT-4 to extract visual concepts.
        """
        prompt = ChatPromptTemplate.from_template(IMAGE_PROMPT_TEMPLATE)
        chain = LLMChain(llm=self.content_generator, prompt=prompt)

        image_prompt = chain.run(content=content, topic=original_prompt, platform=platform)

        return image_prompt.strip()

    def _generate_image(self, image_prompt: str, platform: str) -> str:
        """
        Generate image using Gemini and save to disk.
        Returns path to saved image.

        Note: This is a placeholder implementation.
        The actual Gemini API for image generation may differ.
        """
        # Get platform-specific image dimensions
        width, height = self.platform_specs[platform]["image_size"]

        # TODO: Implement actual Gemini image generation
        # This is pseudocode - actual API call will differ
        try:
            # Generate image with Gemini
            # response = self.image_generator.generate_images(
            #     prompt=image_prompt,
            #     number_of_images=1,
            #     size=f"{width}x{height}"
            # )

            # For now, create placeholder
            image_path = f"generated_images/{platform}_{datetime.now().timestamp()}.jpg"
            os.makedirs("generated_images", exist_ok=True)

            # Save the generated image
            # with open(image_path, 'wb') as f:
            #     f.write(response.images[0].data)

            # Placeholder: Create empty file
            with open(image_path, "w") as f:
                f.write(f"Placeholder for image: {image_prompt}")

            return image_path

        except Exception as e:
            print(f"Error generating image: {e}")
            # Return a placeholder path
            return "placeholder_image.jpg"

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
    print("Social Media Generator - CLI Test")
    print("=" * 50)

    generator = SocialMediaGenerator()

    # Test prompt
    test_prompt = "Announcing our new AI-powered feature that helps teams collaborate better"

    print(f"\nGenerating posts for: {test_prompt}\n")

    # Generate for all platforms
    posts = generator.generate_all_platforms(
        test_prompt,
        context="Focus on productivity and team efficiency",
        brand_voice="innovative and customer-focused",
    )

    # Display results
    for platform, post_data in posts.items():
        if post_data:
            print(f"\n{platform.upper()}")
            print("-" * 50)
            print(f"Content ({len(post_data['content'])} chars):")
            print(post_data["content"])
            print(f"\nImage: {post_data['image_path']}")
            print(f"Image Prompt: {post_data['image_prompt'][:100]}...")
        else:
            print(f"\n{platform.upper()}: FAILED")
