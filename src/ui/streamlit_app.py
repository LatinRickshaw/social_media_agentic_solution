"""
Streamlit Review Interface for Social Media Post Generator

This module provides a web interface for reviewing, editing, and approving
generated social media posts across multiple platforms.

Single Responsibility: UI/UX only - delegates generation to SocialMediaGenerator
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path (must be done before importing src modules)
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st  # noqa: E402

from src.core.brand_voice import BrandVoice  # noqa: E402
from src.core.config import PLATFORM_SPECS, Config  # noqa: E402
from src.core.generator import SocialMediaGenerator  # noqa: E402
from src.data.database import Database  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """
    Initialize Streamlit session state variables.

    Single Responsibility: Session state initialization only
    """
    if "generated_posts" not in st.session_state:
        st.session_state.generated_posts = {}

    if "generator" not in st.session_state:
        st.session_state.generator = SocialMediaGenerator()

    if "brand_voice" not in st.session_state:
        st.session_state.brand_voice = BrandVoice()

    if "generation_in_progress" not in st.session_state:
        st.session_state.generation_in_progress = False


def render_sidebar() -> Dict[str, Any]:
    """
    Render sidebar with generation settings.

    Single Responsibility: Sidebar UI rendering and input collection

    Returns:
        Dict containing user inputs from sidebar
    """
    st.sidebar.header("📝 Post Generation")

    # User prompt input
    user_prompt = st.sidebar.text_area(
        "What would you like to post about?",
        placeholder="E.g., Announcing our new product feature...",
        height=100,
        help="Describe the main topic or message for your social media posts",
    )

    # Context input
    context = st.sidebar.text_area(
        "Additional Context (Optional)",
        placeholder="E.g., Focus on productivity benefits...",
        height=80,
        help="Provide additional context or focus areas",
    )

    # Platform selection
    st.sidebar.subheader("🎯 Target Platforms")
    platforms = {}
    for platform_name in PLATFORM_SPECS.keys():
        platforms[platform_name] = st.sidebar.checkbox(
            platform_name.title(), value=True, help=f"Generate post for {platform_name.title()}"
        )

    # Brand voice option
    use_brand_voice = st.sidebar.checkbox(
        "Use Brand Voice", value=True, help="Apply brand guidelines to generated content"
    )

    # Hashtag option
    include_hashtags = st.sidebar.checkbox(
        "Include Hashtags", value=True, help="Generate platform-optimized hashtags"
    )

    # Generate button
    generate_button = st.sidebar.button(
        "🚀 Generate Posts",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.generation_in_progress,
    )

    return {
        "user_prompt": user_prompt,
        "context": context,
        "platforms": platforms,
        "use_brand_voice": use_brand_voice,
        "include_hashtags": include_hashtags,
        "generate_button": generate_button,
    }


def get_character_count_status(content: str, limit: int) -> tuple:
    """
    Calculate character count and determine status.

    Single Responsibility: Character count calculation

    Args:
        content: Text content to count
        limit: Maximum character limit

    Returns:
        Tuple of (count, status) where status is 'ok', 'warning', or 'error'
    """
    count = len(content)

    if count > limit:
        return count, "error"
    elif limit > count > limit * 0.9:  # Warning at 90-99%
        return count, "warning"
    else:
        return count, "ok"


def render_character_counter(content: str, platform: str):
    """
    Render character counter with visual feedback.

    Single Responsibility: Character count display

    Args:
        content: Text content
        platform: Platform name for limit lookup
    """
    limit = PLATFORM_SPECS[platform]["char_limit"]
    count, status = get_character_count_status(content, limit)

    # Color coding based on status
    if status == "error":
        st.error(f"⚠️ {count:,} / {limit:,} characters - Exceeds limit!")
    elif status == "warning":
        st.warning(f"⚠️ {count:,} / {limit:,} characters - Close to limit")
    else:
        st.info(f"✅ {count:,} / {limit:,} characters")


def render_post_tab(platform: str, post_data: Dict):
    """
    Render a single platform tab with post preview and editing.

    Single Responsibility: Individual platform tab rendering

    Args:
        platform: Platform name
        post_data: Generated post data for the platform
    """
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Content")

        # Editable content
        edited_content = st.text_area(
            "Post Content",
            value=post_data["content"],
            height=200,
            key=f"content_{platform}",
            help="Edit the generated content",
        )

        # Update session state with edited content
        st.session_state.generated_posts[platform]["content"] = edited_content

        # Character counter
        render_character_counter(edited_content, platform)

        # Hashtags section
        if post_data.get("hashtags"):
            st.subheader("🏷️ Hashtags")
            hashtags_text = " ".join(post_data["hashtags"])
            edited_hashtags = st.text_input(
                "Hashtags",
                value=hashtags_text,
                key=f"hashtags_{platform}",
                help="Edit hashtags (space-separated)",
            )
            st.session_state.generated_posts[platform]["hashtags"] = edited_hashtags.split()

    with col2:
        st.subheader("🖼️ Image Preview")

        # Display image
        image_path = post_data.get("image_path")
        if image_path and Path(image_path).exists():
            st.image(image_path, use_container_width=True)

            # Download button
            with open(image_path, "rb") as f:
                st.download_button(
                    label="📥 Download Image",
                    data=f.read(),
                    file_name=Path(image_path).name,
                    mime="image/png",
                    key=f"download_{platform}",
                )
        else:
            st.info("No image generated")

        # Image prompt display
        if post_data.get("image_prompt"):
            with st.expander("🎨 Image Prompt"):
                st.text(post_data["image_prompt"])

    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "🔄 Regenerate Post",
            key=f"regen_post_{platform}",
            use_container_width=True,
            help="Regenerate entire post (content + image)",
        ):
            regenerate_post(platform)

    with col2:
        if st.button(
            "🎨 Regenerate Image",
            key=f"regen_image_{platform}",
            use_container_width=True,
            help="Regenerate image only",
        ):
            regenerate_image(platform)

    with col3:
        if st.button(
            "✅ Approve",
            key=f"approve_{platform}",
            type="primary",
            use_container_width=True,
            help="Approve and save to database",
        ):
            approve_post(platform)

    with col4:
        if st.button(
            "❌ Reject", key=f"reject_{platform}", use_container_width=True, help="Reject this post"
        ):
            reject_post(platform)

    # Metadata expander
    if post_data.get("metadata"):
        with st.expander("ℹ️ Metadata"):
            st.json(post_data["metadata"])


def generate_posts(
    user_prompt: str,
    context: str,
    selected_platforms: List[str],
    use_brand_voice: bool,
    include_hashtags: bool,
):
    """
    Generate posts for selected platforms.

    Single Responsibility: Post generation orchestration

    Args:
        user_prompt: User's content prompt
        context: Additional context
        selected_platforms: List of platform names
        use_brand_voice: Whether to use brand voice
        include_hashtags: Whether to include hashtags
    """
    if not selected_platforms:
        st.error("⚠️ Please select at least one platform")
        return

    if not user_prompt.strip():
        st.error("⚠️ Please enter a prompt")
        return

    # Set generation flag
    st.session_state.generation_in_progress = True

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Get brand voice if enabled
        brand_voice = None
        if use_brand_voice:
            brand_voice = st.session_state.brand_voice.get_brand_voice()

        # Generate posts for each selected platform
        total_platforms = len(selected_platforms)
        generated_posts = {}

        for idx, platform in enumerate(selected_platforms):
            status_text.text(f"Generating post for {platform.title()}...")

            try:
                post_data = st.session_state.generator.generate_post(
                    user_prompt=user_prompt,
                    platform=platform,
                    context=context or None,
                    brand_voice=brand_voice,
                    include_hashtags=include_hashtags,
                )
                generated_posts[platform] = post_data
                logger.info(f"Successfully generated post for {platform}")

            except Exception as e:
                logger.error(f"Failed to generate post for {platform}: {e}")
                st.error(f"❌ Failed to generate {platform} post: {str(e)}")

            # Update progress
            progress_bar.progress((idx + 1) / total_platforms)

        # Store in session state
        st.session_state.generated_posts = generated_posts

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Success message
        if generated_posts:
            st.success(f"✅ Successfully generated {len(generated_posts)} post(s)!")

    except Exception as e:
        logger.error(f"Post generation failed: {e}")
        st.error(f"❌ Generation failed: {str(e)}")

    finally:
        st.session_state.generation_in_progress = False


def regenerate_post(platform: str):
    """
    Regenerate entire post for a platform.

    Single Responsibility: Post regeneration

    Args:
        platform: Platform name
    """
    with st.spinner(f"Regenerating {platform.title()} post..."):
        try:
            # Get original prompt from metadata
            original_prompt = st.session_state.generated_posts[platform]["metadata"].get(
                "user_prompt", ""
            )

            # Regenerate
            post_data = st.session_state.generator.generate_post(
                user_prompt=original_prompt,
                platform=platform,
                context=None,
                brand_voice=None,
                include_hashtags=True,
            )

            st.session_state.generated_posts[platform] = post_data
            st.success(f"✅ Regenerated {platform.title()} post!")
            st.rerun()

        except Exception as e:
            logger.error(f"Failed to regenerate post for {platform}: {e}")
            st.error(f"❌ Regeneration failed: {str(e)}")


def regenerate_image(platform: str):
    """
    Regenerate only the image for a platform.

    Single Responsibility: Image regeneration

    Args:
        platform: Platform name
    """
    with st.spinner(f"Regenerating {platform.title()} image..."):
        try:
            post_data = st.session_state.generated_posts[platform]

            # Regenerate image using existing content
            new_image_path, new_image_prompt = st.session_state.generator.regenerate_image(
                content=post_data["content"], platform=platform
            )

            # Update session state
            st.session_state.generated_posts[platform]["image_path"] = new_image_path
            st.session_state.generated_posts[platform]["image_prompt"] = new_image_prompt

            st.success(f"✅ Regenerated {platform.title()} image!")
            st.rerun()

        except Exception as e:
            logger.error(f"Failed to regenerate image for {platform}: {e}")
            st.error(f"❌ Image regeneration failed: {str(e)}")


def approve_post(platform: str):
    """
    Approve and save post to database.

    Single Responsibility: Post approval and persistence

    Args:
        platform: Platform name
    """
    try:
        post_data = st.session_state.generated_posts[platform]

        # Save to database
        with Database() as db:
            post_id = db.save_post(
                user_prompt=post_data["metadata"].get("user_prompt", ""),
                platform=platform,
                content=post_data["content"],
                image_path=post_data.get("image_path"),
                image_prompt=post_data.get("image_prompt"),
                status="approved",
            )

            # Save approval feedback
            db.save_feedback(
                post_id=post_id,
                feedback_type="approved_as_is",
                created_by="streamlit_user",
            )

        logger.info(f"Approved and saved post {post_id} for {platform}")
        st.success(f"✅ Approved {platform.title()} post (ID: {post_id})")

    except Exception as e:
        logger.error(f"Failed to approve post for {platform}: {e}")
        st.error(f"❌ Failed to save post: {str(e)}")


def reject_post(platform: str):
    """
    Reject post (optionally save with rejected status).

    Single Responsibility: Post rejection

    Args:
        platform: Platform name
    """
    try:
        post_data = st.session_state.generated_posts[platform]

        # Optional: Save with rejected status
        rejection_reason = st.text_input(
            "Rejection reason (optional)", key=f"rejection_reason_{platform}"
        )

        if rejection_reason:
            with Database() as db:
                post_id = db.save_post(
                    user_prompt=post_data["metadata"].get("user_prompt", ""),
                    platform=platform,
                    content=post_data["content"],
                    image_path=post_data.get("image_path"),
                    image_prompt=post_data.get("image_prompt"),
                    status="rejected",
                )

                # Save feedback
                db.save_feedback(
                    post_id=post_id,
                    feedback_type="rejected",
                    rejection_reason=rejection_reason,
                    created_by="streamlit_user",
                )

        # Remove from session state
        del st.session_state.generated_posts[platform]

        st.info(f"❌ Rejected {platform.title()} post")
        st.rerun()

    except Exception as e:
        logger.error(f"Failed to reject post for {platform}: {e}")
        st.error(f"❌ Failed to process rejection: {str(e)}")


def main():
    """
    Main application entry point.

    Single Responsibility: Application orchestration
    """
    # Initialize
    initialize_session_state()

    # Validate configuration and warn about missing keys
    validations = Config.validate()
    missing = [name for name, ok in validations.items() if not ok]
    if missing:
        st.warning(f"Missing configuration: {', '.join(missing)}. Check your .env file.")

    # Header
    st.title("📱 Social Media Post Generator")
    st.markdown("Generate, review, and approve social media posts across multiple platforms")

    # Render sidebar and get inputs
    inputs = render_sidebar()

    # Handle generation
    if inputs["generate_button"]:
        selected_platforms = [
            platform for platform, selected in inputs["platforms"].items() if selected
        ]

        generate_posts(
            user_prompt=inputs["user_prompt"],
            context=inputs["context"],
            selected_platforms=selected_platforms,
            use_brand_voice=inputs["use_brand_voice"],
            include_hashtags=inputs["include_hashtags"],
        )

    # Main content area
    if st.session_state.generated_posts:
        st.divider()
        st.header("📋 Review Generated Posts")

        # Create tabs for each generated platform
        platform_names = list(st.session_state.generated_posts.keys())
        tabs = st.tabs([p.title() for p in platform_names])

        for tab, platform in zip(tabs, platform_names):
            with tab:
                render_post_tab(platform, st.session_state.generated_posts[platform])
    else:
        # Empty state
        st.info(
            "👆 Configure your post settings in the sidebar and click 'Generate Posts' to begin"
        )

        # Show platform specs
        with st.expander("📊 Platform Specifications"):
            for platform, specs in PLATFORM_SPECS.items():
                st.subheader(platform.title())
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Character Limit", f"{specs['char_limit']:,}")
                with col2:
                    st.metric("Image Size", f"{specs['image_size'][0]}×{specs['image_size'][1]}")
                with col3:
                    st.metric("Max Hashtags", specs["max_hashtags"])
                st.caption(f"**Tone:** {specs['tone']}")
                st.divider()


if __name__ == "__main__":
    main()
