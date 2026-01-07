# Social Media Post Generator - Project Specification

**Date Created:** January 7, 2026
**Purpose:** Multi-platform social media content generation using best-of-breed AI models
**Target:** Production-ready system with human-in-loop review transitioning to automated publishing

---

## Project Overview

### Objective
Build a system that takes a user's prompt and generates platform-optimized social media posts with accompanying images, using ChatGPT-4 for content generation and Google Gemini for image generation.

### Target Platforms
1. LinkedIn (Professional networking)
2. Facebook (Community engagement)
3. Twitter/X (Quick updates)
4. Nextdoor (Local community)

### Key Requirements
- **Volume:** Minimum 1 post per day across all platforms (4 posts/day total)
- **Team Capability:** Full software development capability
- **Review Process:**
  - Phase 1: Human review and curation
  - End Goal: Automated hands-off publishing
- **Multi-Provider:** Leverage different AI providers for their strengths

---

## Technical Architecture Decision

### Chosen Approach: Custom LangChain-Based System

**Rationale:**
- Need to mix providers (OpenAI + Google)
- Full development capability available
- Require customization and learning capabilities
- Cost-effective compared to enterprise tools (~$100/month vs $500+/month)

### Core Technology Stack

```
Frontend/Interface Layer:
- Streamlit (Phase 1 - Quick MVP)
- React + FastAPI (Phase 2 - Production)

Orchestration Layer:
- LangChain (Multi-model orchestration)
- Python 3.10+

AI Models:
- OpenAI GPT-4 (Content generation)
- Google Gemini Imagen (Image generation)

Data Layer:
- PostgreSQL (Posts, feedback, metrics)
- AWS S3 / CloudFlare R2 (Image storage)

Publishing Layer:
- LinkedIn API
- Facebook Graph API
- Twitter/X API v2
- Nextdoor (Manual initially, pending API availability)

Scheduling:
- APScheduler or Celery + Redis

Infrastructure:
- Docker containers
- AWS/DigitalOcean/GCP hosting
```

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  User Interface                      │
│           (Streamlit → React + FastAPI)             │
│                                                      │
│  • Input prompt                                      │
│  • Review generated content                          │
│  • Approve/Edit/Regenerate                          │
│  • Schedule posts                                    │
│  • Analytics dashboard                               │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Orchestration Layer                     │
│                  (LangChain)                         │
│                                                      │
│  • Platform-specific prompt templates               │
│  • Content generation pipeline                       │
│  • Image generation pipeline                         │
│  • Platform adapters                                 │
│  • Quality checkers                                  │
│  • Confidence scoring                                │
└─────────────────────────────────────────────────────┘
                         ↓
┌──────────────┬──────────────┬─────────────┬─────────┐
│   ChatGPT-4  │ Gemini Imagen│  Database   │ Storage │
│   (OpenAI)   │   (Google)   │ (Postgres)  │  (S3)   │
│              │              │             │         │
│ • Text gen   │ • Image gen  │ • Posts     │ • Images│
│ • Moderation │ • Multiple   │ • Feedback  │ • Assets│
│              │   styles     │ • Metrics   │         │
└──────────────┴──────────────┴─────────────┴─────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│             Publishing Layer                         │
│                                                      │
│  • LinkedIn API (100 posts/day limit)               │
│  • Facebook Graph API                                │
│  • Twitter/X API (300 posts/3hr limit)              │
│  • Nextdoor (Manual/Email initially)                │
│  • Scheduler (APScheduler/Celery)                   │
│  • Retry logic & error handling                      │
└─────────────────────────────────────────────────────┘
```

---

## Platform Specifications

### Character Limits & Image Requirements

```python
PLATFORM_SPECS = {
    "linkedin": {
        "char_limit": 3000,
        "optimal_length": "150-300 words",
        "image_size": (1200, 627),  # 1.91:1 ratio
        "image_format": "PNG/JPG",
        "max_hashtags": 5,
        "tone": "Professional, insightful",
        "api_rate_limit": "100 posts/day per person"
    },
    "twitter": {
        "char_limit": 280,
        "optimal_length": "200-270 characters",
        "image_size": (1200, 675),  # 16:9 ratio
        "image_format": "PNG/JPG/GIF",
        "max_hashtags": 2,
        "tone": "Conversational, punchy",
        "api_rate_limit": "300 posts/3 hours"
    },
    "facebook": {
        "char_limit": 63206,
        "optimal_length": "100-200 words",
        "image_size": (1200, 630),  # 1.91:1 ratio
        "image_format": "PNG/JPG",
        "max_hashtags": 5,
        "tone": "Friendly, engaging",
        "api_rate_limit": "Varies by page"
    },
    "nextdoor": {
        "char_limit": 5000,
        "optimal_length": "100-250 words",
        "image_size": (1200, 900),  # 4:3 ratio
        "image_format": "JPG/PNG",
        "max_hashtags": 3,
        "tone": "Neighborly, helpful",
        "api_rate_limit": "Limited/no public API"
    }
}
```

### Platform-Specific Prompt Templates

```python
PLATFORM_TEMPLATES = {
    "linkedin": """
Create a professional LinkedIn post about: {topic}

Requirements:
- Professional, thought-leadership tone
- 150-300 words optimal length
- Include 3-5 relevant industry hashtags
- Strong call-to-action at the end
- Provide industry insights or clear value proposition
- Use line breaks for readability
- Optional: Start with a hook/question

Additional context: {context}
Brand voice: {brand_voice}

Format: Plain text with natural paragraph breaks
""",

    "twitter": """
Create an engaging Twitter/X post about: {topic}

Requirements:
- Maximum 280 characters (strict limit)
- Conversational, punchy tone
- Hook in the first sentence
- 1-2 relevant hashtags maximum
- Create urgency or curiosity when appropriate
- Emojis optional but effective when used sparingly

Additional context: {context}
Brand voice: {brand_voice}

Format: Single paragraph, character count must be under 280
""",

    "facebook": """
Create a community-focused Facebook post about: {topic}

Requirements:
- Friendly, conversational tone
- 100-200 words optimal
- Encourage engagement (questions, polls, calls to action)
- 2-4 relevant hashtags
- Authentic and relatable
- Can be slightly more casual than LinkedIn

Additional context: {context}
Brand voice: {brand_voice}

Format: Conversational paragraphs with natural breaks
""",

    "nextdoor": """
Create a neighborhood-friendly Nextdoor post about: {topic}

Requirements:
- Local, community-focused tone
- 100-250 words
- Helpful and genuinely neighborly
- Clear value to local community
- Minimal hashtags (1-2 maximum)
- Emphasis on local benefit or community service
- Avoid heavy sales language

Additional context: {context}
Brand voice: {brand_voice}

Format: Friendly, approachable paragraphs
"""
}
```

---

## Implementation Phases

### Phase 1: Core Pipeline (Weeks 1-3)

**Goal:** Working content and image generation with basic LangChain integration

**Deliverables:**
- Basic Python package structure
- LangChain setup with OpenAI integration
- Google Gemini integration for image generation
- Platform-specific prompt templates
- Sequential pipeline: User Input → GPT-4 → Gemini → Formatted Output
- Basic CLI interface for testing

**Core Components:**

```python
# File: src/core/generator.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
from typing import Dict, List
import os

class SocialMediaGenerator:
    """
    Core generator class that orchestrates content and image generation
    using GPT-4 and Gemini respectively.
    """

    def __init__(self):
        # Initialize OpenAI for content
        self.content_generator = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )

        # Initialize Gemini for images
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.image_generator = genai.GenerativeModel('gemini-pro-vision')

        # Load platform specifications
        self.platform_specs = PLATFORM_SPECS
        self.templates = PLATFORM_TEMPLATES

    def generate_post(self,
                      user_prompt: str,
                      platform: str,
                      context: str = "",
                      brand_voice: str = "professional and engaging") -> Dict:
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
                - image_url: Path to generated image
                - image_prompt: Prompt used for image generation
                - metadata: Platform specs, character count, etc.
        """

        # 1. Generate platform-optimized content
        content = self._generate_content(
            user_prompt,
            platform,
            context,
            brand_voice
        )

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
                "timestamp": datetime.now().isoformat()
            }
        }

        return post_data

    def generate_all_platforms(self,
                               user_prompt: str,
                               context: str = "",
                               brand_voice: str = "professional and engaging") -> Dict[str, Dict]:
        """
        Generate posts for all platforms simultaneously.

        Returns:
            Dict mapping platform name to post data
        """
        posts = {}

        for platform in self.platform_specs.keys():
            try:
                posts[platform] = self.generate_post(
                    user_prompt,
                    platform,
                    context,
                    brand_voice
                )
            except Exception as e:
                print(f"Error generating {platform} post: {e}")
                posts[platform] = None

        return posts

    def _generate_content(self,
                         user_prompt: str,
                         platform: str,
                         context: str,
                         brand_voice: str) -> str:
        """
        Generate platform-specific text content using GPT-4.
        """

        # Create the prompt from template
        template = self.templates[platform]
        prompt = ChatPromptTemplate.from_template(template)

        # Create chain
        chain = LLMChain(llm=self.content_generator, prompt=prompt)

        # Generate content
        result = chain.run(
            topic=user_prompt,
            context=context,
            brand_voice=brand_voice
        )

        # Validate character count
        char_limit = self.platform_specs[platform]["char_limit"]
        if len(result) > char_limit:
            # Truncate and add ellipsis
            result = result[:char_limit-3] + "..."

        return result.strip()

    def _create_image_prompt(self,
                            content: str,
                            platform: str,
                            original_prompt: str) -> str:
        """
        Create an image generation prompt based on the post content.
        Uses GPT-4 to extract visual concepts.
        """

        image_prompt_template = """
Based on this social media post, create a detailed image generation prompt.

Post content:
{content}

Original topic: {topic}

Create a prompt for an image that:
- Visually represents the key concept
- Is appropriate for {platform}
- Is eye-catching and professional
- Avoids text/words in the image
- Uses vibrant, engaging colors

Return only the image generation prompt, nothing else.
"""

        prompt = ChatPromptTemplate.from_template(image_prompt_template)
        chain = LLMChain(llm=self.content_generator, prompt=prompt)

        image_prompt = chain.run(
            content=content,
            topic=original_prompt,
            platform=platform
        )

        return image_prompt.strip()

    def _generate_image(self, image_prompt: str, platform: str) -> str:
        """
        Generate image using Gemini and save to disk.
        Returns path to saved image.
        """

        # Get platform-specific image dimensions
        width, height = self.platform_specs[platform]["image_size"]

        # Generate image with Gemini
        # Note: This is pseudocode - actual Gemini API call will differ
        response = self.image_generator.generate_images(
            prompt=image_prompt,
            number_of_images=1,
            size=f"{width}x{height}"
        )

        # Save image
        image_path = f"generated_images/{platform}_{datetime.now().timestamp()}.jpg"
        os.makedirs("generated_images", exist_ok=True)

        # Save the generated image
        with open(image_path, 'wb') as f:
            f.write(response.images[0].data)

        return image_path
```

**Additional Phase 1 Files:**

```python
# File: src/core/config.py
# Environment configuration and constants

# File: src/core/prompt_templates.py
# All prompt templates centralized

# File: tests/test_generator.py
# Unit tests for core generator

# File: requirements.txt
# Package dependencies

# File: .env.example
# Environment variables template
```

---

### Phase 2: Review Interface (Weeks 3-4)

**Goal:** Build Streamlit UI for human review and approval

**Deliverables:**
- Streamlit web interface
- Post preview with editing capability
- Approve/Reject/Regenerate buttons
- Session state management
- Image preview and download

**Streamlit Application:**

```python
# File: src/ui/streamlit_app.py

import streamlit as st
from PIL import Image
from src.core.generator import SocialMediaGenerator
from src.data.database import Database
import datetime

def main():
    st.set_page_config(
        page_title="Social Media Post Generator",
        page_icon="📱",
        layout="wide"
    )

    # Initialize generator
    if 'generator' not in st.session_state:
        st.session_state.generator = SocialMediaGenerator()

    if 'db' not in st.session_state:
        st.session_state.db = Database()

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")

        brand_voice = st.text_input(
            "Brand Voice",
            value="professional and engaging",
            help="Describe your desired brand voice/tone"
        )

        context = st.text_area(
            "Additional Context",
            help="Any specific requirements, offers, or details to include"
        )

        st.divider()

        # Platform selection
        st.subheader("Target Platforms")
        platforms = {}
        platforms['linkedin'] = st.checkbox("LinkedIn", value=True)
        platforms['twitter'] = st.checkbox("Twitter/X", value=True)
        platforms['facebook'] = st.checkbox("Facebook", value=True)
        platforms['nextdoor'] = st.checkbox("Nextdoor", value=True)

    # Main content
    st.title("📱 Social Media Post Generator")
    st.markdown("Generate optimized posts for multiple platforms using AI")

    # Input section
    st.subheader("1. Enter Your Post Idea")
    user_prompt = st.text_area(
        "What do you want to post about?",
        height=100,
        placeholder="E.g., Announcing our new product launch with 20% discount for early adopters"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_button = st.button("🚀 Generate Posts", type="primary", use_container_width=True)
    with col2:
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.posts = None
            st.rerun()

    # Generate posts
    if generate_button and user_prompt:
        with st.spinner("🎨 Generating your posts..."):
            try:
                # Filter selected platforms
                selected_platforms = [p for p, selected in platforms.items() if selected]

                # Generate posts
                posts = {}
                for platform in selected_platforms:
                    posts[platform] = st.session_state.generator.generate_post(
                        user_prompt,
                        platform,
                        context=context,
                        brand_voice=brand_voice
                    )

                st.session_state.posts = posts
                st.session_state.user_prompt = user_prompt
                st.success(f"✅ Generated {len(posts)} posts!")

            except Exception as e:
                st.error(f"❌ Error generating posts: {str(e)}")

    # Review section
    if 'posts' in st.session_state and st.session_state.posts:
        st.divider()
        st.subheader("2. Review & Edit Generated Posts")

        # Create tabs for each platform
        tabs = st.tabs([p.title() for p in st.session_state.posts.keys()])

        for tab, (platform, post_data) in zip(tabs, st.session_state.posts.items()):
            with tab:
                render_post_review(platform, post_data, st.session_state.db)

def render_post_review(platform, post_data, db):
    """Render the review interface for a single platform post"""

    if post_data is None:
        st.error(f"Failed to generate {platform} post")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### 📝 {platform.title()} Post")

        # Editable content
        edited_content = st.text_area(
            "Post Content",
            value=post_data['content'],
            height=200,
            key=f"{platform}_content"
        )

        # Character count
        char_count = len(edited_content)
        char_limit = post_data['metadata']['char_limit']

        if char_count > char_limit:
            st.error(f"⚠️ {char_count}/{char_limit} characters (over limit!)")
        else:
            st.info(f"📊 {char_count}/{char_limit} characters")

        # Image prompt used
        with st.expander("🎨 View Image Generation Prompt"):
            st.text(post_data['image_prompt'])

    with col2:
        st.markdown("### 🖼️ Generated Image")

        # Display image
        try:
            image = Image.open(post_data['image_path'])
            st.image(image, use_container_width=True)

            # Image download
            with open(post_data['image_path'], 'rb') as f:
                st.download_button(
                    label="⬇️ Download Image",
                    data=f,
                    file_name=f"{platform}_image.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Error loading image: {e}")

    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(f"✅ Approve", key=f"approve_{platform}", use_container_width=True, type="primary"):
            # Save to database as approved
            post_id = db.save_post(
                user_prompt=st.session_state.user_prompt,
                platform=platform,
                content=edited_content,
                image_path=post_data['image_path'],
                image_prompt=post_data['image_prompt'],
                status='approved',
                human_edits=edited_content if edited_content != post_data['content'] else None
            )
            st.success(f"✅ {platform.title()} post approved!")
            st.balloons()

    with col2:
        if st.button(f"🔄 Regenerate", key=f"regen_{platform}", use_container_width=True):
            with st.spinner(f"Regenerating {platform} post..."):
                new_post = st.session_state.generator.generate_post(
                    st.session_state.user_prompt,
                    platform
                )
                st.session_state.posts[platform] = new_post
                st.rerun()

    with col3:
        if st.button(f"🎨 New Image", key=f"reimg_{platform}", use_container_width=True):
            with st.spinner(f"Generating new image..."):
                # Regenerate just the image
                image_prompt = st.session_state.generator._create_image_prompt(
                    edited_content,
                    platform,
                    st.session_state.user_prompt
                )
                image_path = st.session_state.generator._generate_image(image_prompt, platform)
                st.session_state.posts[platform]['image_path'] = image_path
                st.session_state.posts[platform]['image_prompt'] = image_prompt
                st.rerun()

    with col4:
        if st.button(f"❌ Reject", key=f"reject_{platform}", use_container_width=True):
            # Save rejection feedback
            db.save_feedback(
                platform=platform,
                feedback_type='rejected',
                rejection_reason=st.text_input(f"Reason for rejection (optional)", key=f"reject_reason_{platform}")
            )
            st.warning(f"❌ {platform.title()} post rejected")

if __name__ == "__main__":
    main()
```

---

### Phase 3: Database & Logging (Weeks 4-5)

**Goal:** Persist all generated content for learning and analytics

**Database Schema:**

```sql
-- File: src/data/schema.sql

-- Main posts table
CREATE TABLE IF NOT EXISTS generated_posts (
    id SERIAL PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    generated_content TEXT NOT NULL,
    final_content TEXT, -- After human edits
    image_url TEXT,
    image_prompt TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Status: draft, approved, published, rejected, scheduled
    human_edits TEXT, -- JSON of what changed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    scheduled_for TIMESTAMP
);

-- Feedback on posts
CREATE TABLE IF NOT EXISTS post_feedback (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    -- Types: approved_as_is, approved_with_edits, rejected, regenerated
    edit_details JSONB, -- What was changed
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) -- User who gave feedback
);

-- Performance metrics from platforms
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality check results
CREATE TABLE IF NOT EXISTS quality_checks (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    check_type VARCHAR(50) NOT NULL,
    -- Types: appropriateness, brand_alignment, grammar, engagement_potential
    passed BOOLEAN,
    score FLOAT, -- 0.0 to 1.0
    details JSONB,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Publishing log
CREATE TABLE IF NOT EXISTS publishing_log (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255), -- ID from platform API
    status VARCHAR(50) NOT NULL, -- success, failed, retrying
    error_message TEXT,
    attempts INTEGER DEFAULT 1,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_posts_platform ON generated_posts(platform);
CREATE INDEX idx_posts_status ON generated_posts(status);
CREATE INDEX idx_posts_created ON generated_posts(created_at);
CREATE INDEX idx_posts_published ON generated_posts(published_at);
CREATE INDEX idx_metrics_post ON performance_metrics(post_id);
CREATE INDEX idx_feedback_post ON post_feedback(post_id);
```

**Database Interface:**

```python
# File: src/data/database.py

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Dict, List, Optional
import os
from datetime import datetime

class Database:
    """Database interface for the social media generator"""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'social_media_gen'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            cursor_factory=RealDictCursor
        )

    def save_post(self,
                  user_prompt: str,
                  platform: str,
                  content: str,
                  image_path: str,
                  image_prompt: str,
                  status: str = 'draft',
                  human_edits: Optional[str] = None,
                  generated_content: Optional[str] = None) -> int:
        """
        Save a generated post to the database.
        Returns the post ID.
        """

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO generated_posts
                (user_prompt, platform, generated_content, final_content,
                 image_url, image_prompt, status, human_edits)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_prompt,
                platform,
                generated_content or content,
                content,
                image_path,
                image_prompt,
                status,
                human_edits
            ))

            post_id = cur.fetchone()['id']
            self.conn.commit()

            return post_id

    def save_feedback(self,
                      post_id: int,
                      feedback_type: str,
                      edit_details: Optional[Dict] = None,
                      rejection_reason: Optional[str] = None,
                      created_by: str = 'system'):
        """Save feedback on a post"""

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO post_feedback
                (post_id, feedback_type, edit_details, rejection_reason, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                post_id,
                feedback_type,
                Json(edit_details) if edit_details else None,
                rejection_reason,
                created_by
            ))

            self.conn.commit()

    def update_post_status(self, post_id: int, status: str):
        """Update the status of a post"""

        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE generated_posts
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, post_id))

            self.conn.commit()

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Retrieve a post by ID"""

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM generated_posts WHERE id = %s
            """, (post_id,))

            return cur.fetchone()

    def get_approved_posts(self,
                          platform: Optional[str] = None,
                          limit: int = 50) -> List[Dict]:
        """Get approved posts, optionally filtered by platform"""

        with self.conn.cursor() as cur:
            query = """
                SELECT * FROM generated_posts
                WHERE status = 'approved'
            """
            params = []

            if platform:
                query += " AND platform = %s"
                params.append(platform)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()

    def save_performance_metrics(self,
                                post_id: int,
                                platform: str,
                                metrics: Dict):
        """Save performance metrics from platform"""

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO performance_metrics
                (post_id, platform, likes, comments, shares,
                 impressions, clicks, engagement_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                post_id,
                platform,
                metrics.get('likes', 0),
                metrics.get('comments', 0),
                metrics.get('shares', 0),
                metrics.get('impressions', 0),
                metrics.get('clicks', 0),
                metrics.get('engagement_rate', 0.0)
            ))

            self.conn.commit()

    def get_best_performing_posts(self,
                                 platform: Optional[str] = None,
                                 limit: int = 10) -> List[Dict]:
        """Get top performing posts by engagement rate"""

        with self.conn.cursor() as cur:
            query = """
                SELECT
                    gp.*,
                    pm.engagement_rate,
                    pm.likes,
                    pm.comments,
                    pm.shares
                FROM generated_posts gp
                JOIN performance_metrics pm ON gp.id = pm.post_id
                WHERE gp.status = 'published'
            """
            params = []

            if platform:
                query += " AND gp.platform = %s"
                params.append(platform)

            query += " ORDER BY pm.engagement_rate DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()

    def get_analytics_summary(self,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict:
        """Get summary analytics"""

        with self.conn.cursor() as cur:
            query = """
                SELECT
                    COUNT(*) as total_posts,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
                    platform,
                    AVG(CASE
                        WHEN generated_content IS NOT NULL AND final_content IS NOT NULL
                        THEN 1
                        ELSE 0
                    END) as edit_rate
                FROM generated_posts
            """
            params = []

            if start_date:
                query += " WHERE created_at >= %s"
                params.append(start_date)

                if end_date:
                    query += " AND created_at <= %s"
                    params.append(end_date)
            elif end_date:
                query += " WHERE created_at <= %s"
                params.append(end_date)

            query += " GROUP BY platform"

            cur.execute(query, params)
            return cur.fetchall()

    def close(self):
        """Close database connection"""
        self.conn.close()
```

---

### Phase 4: Publishing Integration (Weeks 5-7)

**Goal:** Integrate with platform APIs and build scheduling system

**Platform Publisher:**

```python
# File: src/publishing/publisher.py

from typing import Dict, Optional
from datetime import datetime
import os
import tweepy
from linkedin_v2 import linkedin
import facebook

class PlatformPublisher:
    """
    Handles publishing to all social media platforms.
    Manages API connections, rate limits, and error handling.
    """

    def __init__(self):
        # Initialize LinkedIn
        self.linkedin = linkedin.LinkedInApplication(
            token=os.getenv('LINKEDIN_ACCESS_TOKEN')
        )

        # Initialize Facebook
        self.facebook = facebook.GraphAPI(
            access_token=os.getenv('FACEBOOK_ACCESS_TOKEN')
        )

        # Initialize Twitter/X
        twitter_auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        twitter_auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_SECRET')
        )
        self.twitter = tweepy.API(twitter_auth)

        # Nextdoor - manual for now
        self.nextdoor = None

    def publish_post(self,
                    platform: str,
                    content: str,
                    image_path: str,
                    post_id: int,
                    scheduled_time: Optional[datetime] = None) -> Dict:
        """
        Publish a post to specified platform.

        Args:
            platform: Target platform
            content: Post text content
            image_path: Path to image file
            post_id: Database post ID for logging
            scheduled_time: Optional future publish time

        Returns:
            Dict with status and platform post ID
        """

        if scheduled_time and scheduled_time > datetime.now():
            # Schedule for later
            return self._schedule_post(
                platform, content, image_path, post_id, scheduled_time
            )

        # Publish immediately
        return self._publish_to_platform(platform, content, image_path, post_id)

    def _publish_to_platform(self,
                            platform: str,
                            content: str,
                            image_path: str,
                            post_id: int) -> Dict:
        """Internal method to publish to specific platform"""

        try:
            if platform == "linkedin":
                result = self._publish_linkedin(content, image_path)

            elif platform == "twitter":
                result = self._publish_twitter(content, image_path)

            elif platform == "facebook":
                result = self._publish_facebook(content, image_path)

            elif platform == "nextdoor":
                return {
                    'status': 'manual',
                    'message': 'Nextdoor requires manual posting'
                }

            else:
                raise ValueError(f"Unsupported platform: {platform}")

            # Log success
            self._log_publication(post_id, platform, result, 'success')

            return {
                'status': 'success',
                'platform_post_id': result.get('id'),
                'url': result.get('url')
            }

        except Exception as e:
            # Log error
            self._log_publication(post_id, platform, None, 'failed', str(e))

            return {
                'status': 'failed',
                'error': str(e)
            }

    def _publish_linkedin(self, content: str, image_path: str) -> Dict:
        """Publish to LinkedIn"""

        # Upload image first
        image_urn = self.linkedin.upload_image(image_path)

        # Create post
        post = self.linkedin.submit_share(
            comment=content,
            content={
                'content-url': image_urn,
                'title': 'Post Image',
            },
            visibility_code='public'
        )

        return {
            'id': post.get('updateKey'),
            'url': post.get('updateUrl')
        }

    def _publish_twitter(self, content: str, image_path: str) -> Dict:
        """Publish to Twitter/X"""

        # Upload media
        media = self.twitter.media_upload(image_path)

        # Post tweet
        tweet = self.twitter.update_status(
            status=content,
            media_ids=[media.media_id]
        )

        return {
            'id': tweet.id_str,
            'url': f"https://twitter.com/user/status/{tweet.id_str}"
        }

    def _publish_facebook(self, content: str, image_path: str) -> Dict:
        """Publish to Facebook"""

        # Get page ID
        page_id = os.getenv('FACEBOOK_PAGE_ID')

        # Upload photo with message
        with open(image_path, 'rb') as image_file:
            response = self.facebook.put_photo(
                image=image_file,
                message=content,
                album_path=f"{page_id}/photos"
            )

        return {
            'id': response.get('id'),
            'url': f"https://facebook.com/{response.get('id')}"
        }

    def _schedule_post(self,
                      platform: str,
                      content: str,
                      image_path: str,
                      post_id: int,
                      scheduled_time: datetime) -> Dict:
        """Schedule a post for future publication"""

        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()

        scheduler.add_job(
            self._publish_to_platform,
            'date',
            run_date=scheduled_time,
            args=[platform, content, image_path, post_id],
            id=f"{platform}_{post_id}"
        )

        scheduler.start()

        return {
            'status': 'scheduled',
            'scheduled_for': scheduled_time.isoformat()
        }

    def _log_publication(self,
                        post_id: int,
                        platform: str,
                        result: Optional[Dict],
                        status: str,
                        error_message: Optional[str] = None):
        """Log publication attempt to database"""

        from src.data.database import Database

        db = Database()

        with db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO publishing_log
                (post_id, platform, platform_post_id, status, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                post_id,
                platform,
                result.get('id') if result else None,
                status,
                error_message
            ))

            db.conn.commit()

        # Update post status
        if status == 'success':
            db.update_post_status(post_id, 'published')

        db.close()

    def get_post_metrics(self, platform: str, platform_post_id: str) -> Dict:
        """
        Fetch performance metrics from platform.
        Should be run periodically to track engagement.
        """

        try:
            if platform == "linkedin":
                return self._get_linkedin_metrics(platform_post_id)
            elif platform == "twitter":
                return self._get_twitter_metrics(platform_post_id)
            elif platform == "facebook":
                return self._get_facebook_metrics(platform_post_id)
            else:
                return {}

        except Exception as e:
            print(f"Error fetching metrics for {platform}: {e}")
            return {}

    def _get_linkedin_metrics(self, post_id: str) -> Dict:
        """Fetch LinkedIn post metrics"""
        stats = self.linkedin.get_network_statistics(post_id)

        return {
            'likes': stats.get('numLikes', 0),
            'comments': stats.get('numComments', 0),
            'shares': stats.get('numShares', 0),
            'impressions': stats.get('numImpressions', 0)
        }

    def _get_twitter_metrics(self, tweet_id: str) -> Dict:
        """Fetch Twitter metrics"""
        tweet = self.twitter.get_status(tweet_id)

        return {
            'likes': tweet.favorite_count,
            'comments': tweet.reply_count if hasattr(tweet, 'reply_count') else 0,
            'shares': tweet.retweet_count,
            'impressions': 0  # Not available in basic API
        }

    def _get_facebook_metrics(self, post_id: str) -> Dict:
        """Fetch Facebook metrics"""
        post = self.facebook.get_object(
            id=post_id,
            fields='likes.summary(true),comments.summary(true),shares'
        )

        return {
            'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
            'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
            'shares': post.get('shares', {}).get('count', 0),
            'impressions': 0  # Requires insights API access
        }
```

**Metrics Collector (Cron Job):**

```python
# File: src/publishing/metrics_collector.py

from src.publishing.publisher import PlatformPublisher
from src.data.database import Database
from datetime import datetime, timedelta

class MetricsCollector:
    """
    Periodically fetch and store post performance metrics.
    Run as a scheduled job (e.g., daily via cron).
    """

    def __init__(self):
        self.publisher = PlatformPublisher()
        self.db = Database()

    def collect_recent_metrics(self, days_back: int = 7):
        """
        Collect metrics for posts published in the last N days.
        """

        cutoff_date = datetime.now() - timedelta(days=days_back)

        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    gp.id,
                    gp.platform,
                    pl.platform_post_id
                FROM generated_posts gp
                JOIN publishing_log pl ON gp.id = pl.post_id
                WHERE gp.status = 'published'
                AND gp.published_at >= %s
                AND pl.status = 'success'
            """, (cutoff_date,))

            posts = cur.fetchall()

        print(f"Collecting metrics for {len(posts)} posts...")

        for post in posts:
            metrics = self.publisher.get_post_metrics(
                post['platform'],
                post['platform_post_id']
            )

            if metrics:
                # Calculate engagement rate
                total_engagement = (
                    metrics.get('likes', 0) +
                    metrics.get('comments', 0) +
                    metrics.get('shares', 0)
                )
                impressions = metrics.get('impressions', 1)
                engagement_rate = total_engagement / impressions if impressions > 0 else 0

                metrics['engagement_rate'] = engagement_rate

                # Save to database
                self.db.save_performance_metrics(
                    post['id'],
                    post['platform'],
                    metrics
                )

                print(f"✅ Updated metrics for {post['platform']} post {post['id']}")

        self.db.close()
        print("Metrics collection complete!")

if __name__ == "__main__":
    collector = MetricsCollector()
    collector.collect_recent_metrics(days_back=7)
```

---

### Phase 5: Quality & Automation (Weeks 7-10)

**Goal:** Add quality checks and confidence-based auto-publishing

**Quality Checker:**

```python
# File: src/quality/checker.py

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict
import os

class QualityChecker:
    """
    Performs multiple quality checks on generated posts
    before publishing. Provides confidence scoring for
    automated publishing decisions.
    """

    def __init__(self):
        self.moderator = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,  # Low temperature for consistency
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )

    def check_post(self,
                   content: str,
                   platform: str,
                   image_path: str = None) -> Dict:
        """
        Run all quality checks on a post.

        Returns:
            Dict with check results and overall confidence score
        """

        checks = {
            "appropriate": self._check_appropriateness(content),
            "on_brand": self._check_brand_alignment(content),
            "platform_fit": self._check_platform_requirements(content, platform),
            "grammar": self._check_grammar(content),
            "engagement_potential": self._predict_engagement(content, platform),
            "image_appropriate": self._check_image_appropriateness(image_path) if image_path else {"passed": True, "score": 1.0}
        }

        # Calculate overall confidence score
        confidence_score = self._calculate_confidence(checks)

        return {
            "checks": checks,
            "confidence_score": confidence_score,
            "recommendation": self._get_recommendation(confidence_score)
        }

    def _check_appropriateness(self, content: str) -> Dict:
        """Check for offensive or inappropriate content"""

        prompt = ChatPromptTemplate.from_template("""
Review this social media post for content appropriateness.

Post: {content}

Check for:
1. Offensive language or slurs
2. Controversial political statements
3. Misinformation or unverified claims
4. Brand safety issues
5. Potential legal issues

Return ONLY a JSON object with this structure:
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "issues": ["list of any issues found"],
  "recommendation": "brief recommendation"
}}
""")

        response = self.moderator.predict(prompt.format(content=content))

        # Parse JSON response
        import json
        try:
            result = json.loads(response)
        except:
            result = {
                "passed": True,
                "score": 0.8,
                "issues": [],
                "recommendation": "Unable to parse check results"
            }

        return result

    def _check_brand_alignment(self, content: str) -> Dict:
        """Check if content aligns with brand voice and values"""

        # Load brand guidelines (would come from config/database)
        brand_guidelines = """
        Brand Voice: Professional, friendly, helpful
        Values: Innovation, customer-first, transparency
        Avoid: Jargon, hype, aggressive sales language
        """

        prompt = ChatPromptTemplate.from_template("""
Review this social media post for brand alignment.

Post: {content}

Brand Guidelines:
{brand_guidelines}

Evaluate if the post:
1. Matches the brand voice
2. Reflects brand values
3. Avoids prohibited language/tone
4. Would resonate with target audience

Return ONLY a JSON object:
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "alignment_notes": "brief notes",
  "recommendation": "brief recommendation"
}}
""")

        response = self.moderator.predict(
            prompt.format(
                content=content,
                brand_guidelines=brand_guidelines
            )
        )

        import json
        try:
            result = json.loads(response)
        except:
            result = {"passed": True, "score": 0.7}

        return result

    def _check_platform_requirements(self, content: str, platform: str) -> Dict:
        """Check if post meets platform-specific requirements"""

        from src.core.generator import PLATFORM_SPECS
        specs = PLATFORM_SPECS[platform]

        checks = {
            "char_limit": len(content) <= specs["char_limit"],
            "char_count": len(content),
            "char_limit_value": specs["char_limit"]
        }

        # Check hashtag count
        hashtag_count = content.count('#')
        checks["hashtag_count"] = hashtag_count
        checks["hashtag_limit"] = specs["max_hashtags"]
        checks["hashtags_ok"] = hashtag_count <= specs["max_hashtags"]

        # Overall pass
        checks["passed"] = checks["char_limit"] and checks["hashtags_ok"]
        checks["score"] = 1.0 if checks["passed"] else 0.5

        return checks

    def _check_grammar(self, content: str) -> Dict:
        """Check for grammar and spelling issues"""

        prompt = ChatPromptTemplate.from_template("""
Review this text for grammar and spelling errors.

Text: {content}

Return ONLY a JSON object:
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "errors": ["list of errors found"],
  "severity": "none/minor/major"
}}
""")

        response = self.moderator.predict(prompt.format(content=content))

        import json
        try:
            result = json.loads(response)
        except:
            result = {"passed": True, "score": 0.9, "errors": []}

        return result

    def _predict_engagement(self, content: str, platform: str) -> Dict:
        """Predict likely engagement based on content quality"""

        prompt = ChatPromptTemplate.from_template("""
Predict the engagement potential of this {platform} post.

Post: {content}

Consider:
1. Hook/opening strength
2. Value provided to reader
3. Call-to-action clarity
4. Emotional appeal
5. Relevance to platform audience

Return ONLY a JSON object:
{{
  "score": 0.0-1.0,
  "prediction": "low/medium/high",
  "strengths": ["list strengths"],
  "improvements": ["suggested improvements"]
}}
""")

        response = self.moderator.predict(
            prompt.format(content=content, platform=platform)
        )

        import json
        try:
            result = json.loads(response)
            result["passed"] = result["score"] >= 0.6
        except:
            result = {"passed": True, "score": 0.7, "prediction": "medium"}

        return result

    def _check_image_appropriateness(self, image_path: str) -> Dict:
        """Check if image is appropriate (placeholder for future vision model)"""

        # In production, this would use a vision model to check:
        # - Image quality
        # - Appropriateness
        # - Relevance to content

        # For now, basic checks
        import os
        from PIL import Image

        if not os.path.exists(image_path):
            return {"passed": False, "score": 0.0, "reason": "Image not found"}

        try:
            img = Image.open(image_path)

            # Basic quality checks
            width, height = img.size

            checks = {
                "passed": width >= 600 and height >= 400,
                "score": 1.0 if width >= 600 and height >= 400 else 0.6,
                "width": width,
                "height": height,
                "format": img.format
            }

            return checks

        except Exception as e:
            return {"passed": False, "score": 0.0, "error": str(e)}

    def _calculate_confidence(self, checks: Dict) -> float:
        """
        Calculate overall confidence score from all checks.
        Weighted average of check scores.
        """

        weights = {
            "appropriate": 0.25,  # Most important
            "on_brand": 0.20,
            "platform_fit": 0.15,
            "grammar": 0.15,
            "engagement_potential": 0.15,
            "image_appropriate": 0.10
        }

        total_score = 0.0
        total_weight = 0.0

        for check_name, weight in weights.items():
            if check_name in checks:
                check_result = checks[check_name]
                score = check_result.get("score", 0.5)
                total_score += score * weight
                total_weight += weight

        confidence = total_score / total_weight if total_weight > 0 else 0.5

        return round(confidence, 3)

    def _get_recommendation(self, confidence_score: float) -> str:
        """
        Get publishing recommendation based on confidence score.

        Thresholds:
        - >= 0.85: Auto-publish
        - >= 0.60: Human review
        - < 0.60: Block or regenerate
        """

        if confidence_score >= 0.85:
            return "auto_publish"
        elif confidence_score >= 0.60:
            return "human_review"
        else:
            return "regenerate"
```

**Automation Decision Engine:**

```python
# File: src/automation/decision_engine.py

from src.quality.checker import QualityChecker
from src.data.database import Database
from src.publishing.publisher import PlatformPublisher
from typing import Dict, List
import numpy as np

class AutomationDecisionEngine:
    """
    Decides whether posts can be auto-published based on:
    - Quality check scores
    - Historical performance
    - Similarity to approved content
    """

    def __init__(self):
        self.quality_checker = QualityChecker()
        self.db = Database()
        self.publisher = PlatformPublisher()

    def evaluate_post(self,
                     content: str,
                     platform: str,
                     image_path: str,
                     user_prompt: str) -> Dict:
        """
        Evaluate if a post should be auto-published.

        Returns:
            Dict with decision and reasoning
        """

        # Run quality checks
        quality_results = self.quality_checker.check_post(
            content, platform, image_path
        )

        # Get historical performance for similar content
        historical_score = self._get_historical_similarity_score(
            content, platform
        )

        # Calculate final decision score
        final_score = self._calculate_decision_score(
            quality_results["confidence_score"],
            historical_score
        )

        # Make decision
        decision = self._make_decision(final_score)

        return {
            "decision": decision,  # auto_publish, human_review, or block
            "confidence_score": quality_results["confidence_score"],
            "historical_score": historical_score,
            "final_score": final_score,
            "quality_checks": quality_results["checks"],
            "reasoning": self._explain_decision(decision, final_score, quality_results)
        }

    def _get_historical_similarity_score(self,
                                        content: str,
                                        platform: str) -> float:
        """
        Compare content to previously approved posts.
        Returns similarity score 0.0-1.0
        """

        # Get top performing posts for this platform
        best_posts = self.db.get_best_performing_posts(platform, limit=20)

        if not best_posts:
            return 0.5  # Neutral if no history

        # Simple similarity check (in production, use embeddings)
        similarities = []

        for post in best_posts:
            # Calculate simple word overlap
            content_words = set(content.lower().split())
            post_words = set(post['final_content'].lower().split())

            if len(content_words) == 0:
                continue

            overlap = len(content_words & post_words)
            similarity = overlap / len(content_words)

            # Weight by engagement rate
            engagement_weight = post.get('engagement_rate', 0.1)
            weighted_similarity = similarity * (1 + engagement_weight)

            similarities.append(weighted_similarity)

        if not similarities:
            return 0.5

        # Return average similarity
        avg_similarity = np.mean(similarities)

        # Normalize to 0-1 range
        return min(1.0, avg_similarity)

    def _calculate_decision_score(self,
                                 quality_score: float,
                                 historical_score: float) -> float:
        """
        Combine quality and historical scores.
        Weights quality more heavily initially.
        """

        # Get count of published posts to adjust weights
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as count
                FROM generated_posts
                WHERE status = 'published'
            """)
            published_count = cur.fetchone()['count']

        # Initially weight quality more, gradually increase historical weight
        quality_weight = max(0.6, 0.9 - (published_count * 0.01))
        historical_weight = 1 - quality_weight

        final_score = (
            quality_score * quality_weight +
            historical_score * historical_weight
        )

        return round(final_score, 3)

    def _make_decision(self, final_score: float) -> str:
        """
        Make auto-publish decision based on final score.

        Thresholds:
        - >= 0.85: Auto-publish
        - >= 0.60: Human review
        - < 0.60: Block/regenerate
        """

        if final_score >= 0.85:
            return "auto_publish"
        elif final_score >= 0.60:
            return "human_review"
        else:
            return "block"

    def _explain_decision(self,
                         decision: str,
                         final_score: float,
                         quality_results: Dict) -> str:
        """Generate human-readable explanation of decision"""

        explanations = {
            "auto_publish": f"High confidence (score: {final_score:.2f}). All quality checks passed. Similar to previous successful posts.",
            "human_review": f"Moderate confidence (score: {final_score:.2f}). Passes quality checks but would benefit from human review.",
            "block": f"Low confidence (score: {final_score:.2f}). Quality concerns or insufficient historical data. Recommend regeneration."
        }

        base_explanation = explanations.get(decision, "Unknown decision")

        # Add specific check failures
        failed_checks = [
            check_name
            for check_name, result in quality_results["checks"].items()
            if not result.get("passed", True)
        ]

        if failed_checks:
            base_explanation += f" Failed checks: {', '.join(failed_checks)}."

        return base_explanation

    def process_and_decide(self, post_id: int) -> Dict:
        """
        Full workflow: Load post, evaluate, and take action.
        """

        # Load post from database
        post = self.db.get_post(post_id)

        if not post:
            return {"error": "Post not found"}

        # Evaluate
        evaluation = self.evaluate_post(
            post['final_content'],
            post['platform'],
            post['image_url'],
            post['user_prompt']
        )

        # Take action based on decision
        if evaluation['decision'] == 'auto_publish':
            # Publish automatically
            publish_result = self.publisher.publish_post(
                post['platform'],
                post['final_content'],
                post['image_url'],
                post_id
            )

            evaluation['publish_result'] = publish_result

        elif evaluation['decision'] == 'human_review':
            # Flag for review
            self.db.update_post_status(post_id, 'review_needed')
            evaluation['action'] = 'Flagged for human review'

        else:  # block
            # Mark as needs regeneration
            self.db.update_post_status(post_id, 'needs_regeneration')
            evaluation['action'] = 'Blocked - needs regeneration'

        return evaluation
```

---

## Cost Estimates

### Monthly Operating Costs (4 posts/day = 120 posts/month)

| Item | Calculation | Cost |
|------|-------------|------|
| **OpenAI GPT-4** | 480 API calls × $0.03 | $14.40 |
| **Google Gemini** | 480 images × $0.04 | $19.20 |
| **Database** | PostgreSQL (managed) | $15-25 |
| **Storage** | S3/R2 for images | $5-10 |
| **Hosting** | Server/container hosting | $20-50 |
| **Platform APIs** | LinkedIn, FB, Twitter | Free |
| **Total** | | **$75-120/month** |

**Note:** This is significantly cheaper than enterprise tools ($300-1000/month) while providing more flexibility.

---

## Development Timeline

### Week-by-Week Breakdown

**Weeks 1-2: Foundation**
- Project setup, dependencies
- Core generator class
- OpenAI integration
- Gemini integration
- Basic CLI testing

**Week 3: Platform Optimization**
- Platform-specific templates
- Image size handling
- Character limit validation
- Initial testing

**Week 4: Review Interface**
- Streamlit UI
- Post preview
- Edit/approve workflow
- Session management

**Week 5: Database Layer**
- Schema creation
- Database interface
- Migration scripts
- Logging setup

**Week 6-7: Platform APIs**
- LinkedIn integration
- Twitter integration
- Facebook integration
- Error handling & retries

**Week 8: Scheduling**
- Scheduler setup
- Publishing queue
- Nextdoor workaround
- Testing

**Week 9: Quality System**
- Quality checker implementation
- Brand alignment checks
- Grammar checks

**Week 10: Automation**
- Decision engine
- Confidence scoring
- Historical analysis
- Auto-publish logic

**Weeks 11-12: Polish & Deploy**
- End-to-end testing
- Performance optimization
- Production deployment
- Documentation

**Milestones:**
- Week 3: Working MVP (manual)
- Week 5: Database integration
- Week 7: Can publish to platforms
- Week 10: Full automation capability
- Week 12: Production ready

---

## Project Structure

```
social-media-generator/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── generator.py           # Main generation logic
│   │   ├── config.py               # Configuration
│   │   └── prompt_templates.py    # Prompt templates
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py            # Database interface
│   │   ├── schema.sql             # Database schema
│   │   └── migrations/            # DB migrations
│   │
│   ├── quality/
│   │   ├── __init__.py
│   │   └── checker.py             # Quality checks
│   │
│   ├── automation/
│   │   ├── __init__.py
│   │   └── decision_engine.py     # Auto-publish logic
│   │
│   ├── publishing/
│   │   ├── __init__.py
│   │   ├── publisher.py           # Platform publishers
│   │   └── metrics_collector.py  # Fetch metrics
│   │
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py       # Review interface
│
├── tests/
│   ├── test_generator.py
│   ├── test_database.py
│   ├── test_publisher.py
│   └── test_quality.py
│
├── scripts/
│   ├── setup_db.py                # Initialize database
│   ├── collect_metrics.py         # Cron job script
│   └── deploy.sh                  # Deployment script
│
├── generated_images/              # Image storage (local)
├── config/
│   └── brand_guidelines.yaml      # Brand configuration
│
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── docker-compose.yml            # Local development
├── Dockerfile                     # Production container
├── README.md
└── PROJECT_SPEC.md               # This document
```

---

## Environment Variables

```bash
# File: .env.example

# OpenAI
OPENAI_API_KEY=sk-...

# Google Gemini
GOOGLE_API_KEY=...

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_media_gen
DB_USER=postgres
DB_PASSWORD=...

# LinkedIn
LINKEDIN_ACCESS_TOKEN=...

# Facebook
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...

# Twitter/X
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=social-media-images

# Application
ENV=development
DEBUG=true
```

---

## Key Dependencies

```
# File: requirements.txt

# Core
langchain==0.1.0
openai==1.0.0
google-generativeai==0.3.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# UI
streamlit==1.29.0
pillow==10.1.0

# Publishing
tweepy==4.14.0
python-linkedin-v2==0.1.0
facebook-sdk==3.1.0

# Scheduling
apscheduler==3.10.4
celery==5.3.4
redis==5.0.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0
numpy==1.26.2
```

---

## Nextdoor Considerations

**Challenge:** Nextdoor does not have a robust public API.

**Options:**

1. **Manual Posting (Recommended Initially)**
   - Copy-paste from your tool
   - Add to Nextdoor manually
   - Track as "pending_manual"

2. **Email-to-Nextdoor**
   - Some users report this feature
   - Investigate if available for your account

3. **Nextdoor Business Portal**
   - May have better API access
   - Contact Nextdoor for business accounts

4. **Browser Automation (Not Recommended)**
   - Selenium/Playwright
   - Against Nextdoor TOS
   - High risk of account suspension

**Recommendation:** Start with manual, lobby Nextdoor for API access.

---

## Future Enhancements

### Phase 6+ Ideas

1. **Advanced Analytics Dashboard**
   - React-based analytics UI
   - Post performance comparison
   - A/B testing results
   - Engagement trends

2. **Learning from Feedback**
   - Fine-tune GPT-4 on approved posts
   - Build custom content style model
   - Automatic prompt optimization

3. **Multi-Account Support**
   - Manage multiple brands
   - Different API credentials per brand
   - Brand-specific templates

4. **Content Calendar**
   - Visual calendar interface
   - Drag-and-drop scheduling
   - Theme planning

5. **Collaboration Features**
   - Team review workflows
   - Approval chains
   - Comment threads

6. **Video Support**
   - Generate short videos
   - Add captions
   - Platform-specific formats

7. **Hashtag Optimization**
   - Research trending hashtags
   - Suggest based on content
   - Track hashtag performance

8. **Competitor Analysis**
   - Monitor competitor posts
   - Benchmark performance
   - Identify content gaps

---

## Critical Success Factors

1. **Quality Prompt Templates**
   - Continuously refine templates
   - A/B test variations
   - Platform-specific optimization

2. **Brand Voice Consistency**
   - Clear brand guidelines
   - Quality check thresholds
   - Human review for edge cases

3. **API Reliability**
   - Proper error handling
   - Retry logic
   - Rate limit management

4. **Feedback Loop**
   - Track what works
   - Learn from approvals/rejections
   - Iteratively improve

5. **Gradual Automation**
   - Start with heavy human review
   - Build confidence over time
   - Adjust thresholds based on results

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| API rate limits | Implement queuing, respect limits, cache when possible |
| API downtime | Retry logic, fallback providers, queue system |
| Image generation quality | Multiple prompts, regeneration option, human review |
| Cost overruns | Monitor usage, set alerts, optimize prompts |

### Content Risks

| Risk | Mitigation |
|------|------------|
| Inappropriate content | Multiple quality checks, moderation layer, human review |
| Brand misalignment | Strong brand guidelines, quality checker, approval workflow |
| Factual errors | Source verification, fact-checking step, disclaimers |
| Platform policy violations | Platform-specific checks, stay updated on TOS |

### Operational Risks

| Risk | Mitigation |
|------|------------|
| Manual bottleneck | Gradual automation, parallel review, batch processing |
| Loss of authentic voice | Regular human oversight, quality benchmarks, feedback loop |
| Over-automation | Conservative confidence thresholds, human review for edge cases |

---

## Support & Maintenance

### Daily
- Monitor automated posts
- Check error logs
- Review flagged content

### Weekly
- Analyze performance metrics
- Adjust quality thresholds
- Review rejected posts

### Monthly
- Generate performance reports
- Update brand guidelines
- Fine-tune prompts
- Update dependencies

### Quarterly
- Major feature additions
- Platform API updates
- Security audits
- Cost optimization

---

## Getting Started

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd social-media-generator
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Initialize Database**
   ```bash
   python scripts/setup_db.py
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

5. **Start Development UI**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

6. **Generate Your First Post**
   - Enter a prompt
   - Review generated content
   - Approve or regenerate
   - Schedule or publish

---

## Questions for Claude Code to Start

When you start working with Claude Code, consider these initial tasks:

1. **Phase 1 Setup**
   - Create the basic project structure
   - Set up the core generator class
   - Implement OpenAI integration
   - Create platform-specific prompt templates

2. **Testing Strategy**
   - How should we structure tests?
   - What's the testing workflow?

3. **Database First or API First?**
   - Should we build DB layer before or after basic generation?

4. **Image Generation**
   - What's the best way to handle Gemini API?
   - Should we cache generated images?

5. **Review Interface**
   - Streamlit sufficient or go straight to React?

---

## Contact & Support

**Project Lead:** [Your Name]
**Start Date:** January 7, 2026
**Repository:** [TBD]
**Documentation:** [TBD]

---

## Appendix A: API Documentation References

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [LinkedIn API](https://docs.microsoft.com/linkedin/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Twitter/X API](https://developer.twitter.com/en/docs)
- [LangChain Docs](https://python.langchain.com/docs)

---

## Appendix B: Example Prompts

See `src/core/prompt_templates.py` for production templates.

---

## Version History

- v1.0 (2026-01-07): Initial project specification
- Future versions will track major milestones and changes

---

**End of Project Specification**
