"""
Platform-specific prompt templates for content generation.
"""

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
""",
}

IMAGE_PROMPT_TEMPLATE = """
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

BRAND_ALIGNMENT_TEMPLATE = """
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
"""

APPROPRIATENESS_CHECK_TEMPLATE = """
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
"""

GRAMMAR_CHECK_TEMPLATE = """
Review this text for grammar and spelling errors.

Text: {content}

Return ONLY a JSON object:
{{
  "passed": true/false,
  "score": 0.0-1.0,
  "errors": ["list of errors found"],
  "severity": "none/minor/major"
}}
"""

ENGAGEMENT_PREDICTION_TEMPLATE = """
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
"""
