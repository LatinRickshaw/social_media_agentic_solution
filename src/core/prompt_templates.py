"""
Platform-specific prompt templates for content generation.
"""

PLATFORM_TEMPLATES = {
    "linkedin": """
Create a professional LinkedIn post about: {topic}

BRAND VOICE & TONE:
Your writing must embody this brand voice: {brand_voice}
Primary tone: Professional, thought-leadership style
Approach: Insightful, industry-focused, value-driven

CONTENT REQUIREMENTS:
- Length: 150-300 words (optimal for LinkedIn engagement)
- Structure: Start with a compelling hook or thought-provoking question
- Substance: Provide genuine industry insights or clear value proposition
- Formatting: Use line breaks every 2-3 sentences for scannability
- Call-to-action: End with a strong, professional CTA

HASHTAG STRATEGY:
- Include 3-5 highly relevant industry or trending hashtags
- Place hashtags at the end of the post
- Mix specific industry terms with broader trending topics
- Example format: #IndustryTerm #TrendingTopic #BrandRelevant

WHAT TO AVOID:
- Overly casual language or slang
- Aggressive sales pitch
- Generic buzzwords without substance
- Emoji overuse (1-2 strategic emojis max)

Additional context: {context}

Format: Plain text with natural paragraph breaks. Do not use markdown formatting.
""",
    "twitter": """
Create an engaging Twitter/X post about: {topic}

BRAND VOICE & TONE:
Your writing must embody this brand voice: {brand_voice}
Primary tone: Conversational, punchy, authentic
Approach: Quick-hitting, attention-grabbing, shareable

CONTENT REQUIREMENTS:
- STRICT CHARACTER LIMIT: Maximum 280 characters (including hashtags and spaces)
- Hook: Lead with your strongest point in the first 10 words
- Value: Deliver immediate value or spark curiosity
- Urgency: Create FOMO or drive engagement when appropriate
- Emojis: Use 1-2 relevant emojis strategically (optional but effective)

HASHTAG STRATEGY:
- Use ONLY 1-2 highly targeted hashtags
- Choose trending or niche-specific tags
- Place at the end or naturally within the text
- Count hashtags in your 280-character limit

TWITTER-SPECIFIC TACTICS:
- Front-load the most important information
- Use conversational language that feels authentic
- End with a question to drive replies (optional)
- Make it retweetable - think shareability

WHAT TO AVOID:
- Thread-style multi-tweets (single tweet only)
- Hashtag stuffing (#no #more #than #two)
- Overly promotional language
- Going over 280 characters (this will cause rejection)

Additional context: {context}

Format: Single paragraph. Count characters carefully. Must be under 280 total.
""",
    "facebook": """
Create a community-focused Facebook post about: {topic}

BRAND VOICE & TONE:
Your writing must embody this brand voice: {brand_voice}
Primary tone: Friendly, conversational, relatable
Approach: Community-building, authentic storytelling, engaging

CONTENT REQUIREMENTS:
- Length: 100-200 words (optimal for Facebook feed)
- Opening: Start with a relatable statement or question
- Engagement: Explicitly encourage comments, shares, or reactions
- Storytelling: Use conversational, authentic language
- Call-to-action: Include clear engagement prompt (ask questions, run polls, etc.)
- Formatting: Short paragraphs with natural breaks

HASHTAG STRATEGY:
- Include 2-4 relevant hashtags
- Place at the end of the post
- Mix branded hashtags with popular topics
- Less formal than LinkedIn, more playful options acceptable

FACEBOOK-SPECIFIC TACTICS:
- Ask questions to drive comments
- Use "Tag a friend who..." style prompts
- Reference shared experiences or emotions
- Slightly more casual than LinkedIn (but still professional)
- Emojis are welcome (2-3 relevant ones)

WHAT TO AVOID:
- Corporate jargon
- Overly formal language
- Link-heavy posts (algorithm deprioritizes)
- Clickbait tactics

Additional context: {context}

Format: Conversational paragraphs with natural breaks. Write like you're talking to friends.
""",
    "nextdoor": """
Create a neighborhood-friendly Nextdoor post about: {topic}

BRAND VOICE & TONE:
Your writing must embody this brand voice: {brand_voice}
Primary tone: Neighborly, helpful, locally-focused
Approach: Community service, genuine helpfulness, local value

CONTENT REQUIREMENTS:
- Length: 100-250 words
- Opening: Greet neighbors warmly (e.g., "Hi neighbors!")
- Local focus: Explicitly connect to neighborhood benefit or local community
- Helpfulness: Frame as service or valuable information for locals
- Authenticity: Be genuinely neighborly, not sales-focused
- Call-to-action: Gentle invitation (not aggressive sales pitch)

HASHTAG STRATEGY:
- Minimal hashtags: 1-2 maximum
- Use local area or community-focused tags
- Example: #YourNeighborhood #CommunityFirst
- Hashtags are less important on Nextdoor than other platforms

NEXTDOOR-SPECIFIC TACTICS:
- Emphasize how this helps the local community
- Reference neighborhood-specific benefits
- Use warm, personal language
- Position as a neighbor helping neighbors
- Avoid corporate speak entirely
- Think "local business owner" not "national brand"

WHAT TO AVOID:
- Aggressive sales language or pressure tactics
- Corporate/marketing speak
- Anything not relevant to local community
- Heavy promotion without genuine local value
- Overly promotional tone

Additional context: {context}

Format: Friendly, approachable paragraphs. Write like a helpful neighbor, not a marketer.
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
