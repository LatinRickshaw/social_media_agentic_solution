# Streamlit Review Interface

Web interface for reviewing, editing, and approving generated social media posts.

## Features

- **Multi-Platform Generation**: Generate posts for LinkedIn, Twitter, Facebook, and Nextdoor from a single prompt
- **Content Editing**: Edit generated content with live character count validation
- **Image Management**: Preview images, download them, and regenerate individually
- **Post Actions**: Approve, reject, or regenerate posts
- **Session Management**: Maintains state during review workflow
- **Brand Voice Integration**: Apply brand guidelines automatically
- **Platform Tabs**: Side-by-side comparison of platform-specific posts

## Quick Start

### Prerequisites

Ensure you have:
- Python 3.8+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements.txt`
- Environment variables configured in `.env` (see `.env.example`)

### Running the Application

```bash
# From project root
streamlit run src/ui/streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`

### Alternative Port

```bash
streamlit run src/ui/streamlit_app.py --server.port 8502
```

## Usage

### 1. Generate Posts

**Sidebar Settings:**
- Enter your post topic in the text area
- Optionally add context for more targeted content
- Select target platforms (default: all selected)
- Toggle "Use Brand Voice" to apply brand guidelines
- Toggle "Include Hashtags" to generate platform-optimized hashtags
- Click "🚀 Generate Posts"

### 2. Review Generated Posts

**Platform Tabs:**
Each platform tab displays:
- Editable post content with character count
- Editable hashtags
- Image preview with download button
- Image generation prompt (in expander)
- Post metadata (in expander)

**Character Count:**
- ✅ Green: Within limits
- ⚠️ Yellow: Close to limit (90%+)
- 🔴 Red: Exceeds limit

### 3. Edit Content

- Click in the content text area to edit
- Character count updates in real-time
- Edit hashtags as space-separated values
- Changes are preserved in session state

### 4. Take Action

**Available Actions:**
- **🔄 Regenerate Post**: Regenerate both content and image
- **🎨 Regenerate Image**: Regenerate image only, keep content
- **✅ Approve**: Save post to database with "approved" status
- **❌ Reject**: Remove post (optionally save with "rejected" status)

### 5. Approval Workflow

When you approve a post:
1. Post is saved to `generated_posts` table
2. Status is set to `approved`
3. Post ID is displayed in success message
4. Post is ready for publishing (Phase 3 feature)

## Architecture

### Single Responsibility Design

The application follows SOLID principles with clear separation:

| Function | Responsibility |
|----------|---------------|
| `initialize_session_state()` | Session state initialization |
| `render_sidebar()` | Sidebar UI and input collection |
| `render_post_tab()` | Individual platform tab rendering |
| `render_character_counter()` | Character count display |
| `generate_posts()` | Post generation orchestration |
| `regenerate_post()` | Full post regeneration |
| `regenerate_image()` | Image-only regeneration |
| `approve_post()` | Post approval and persistence |
| `reject_post()` | Post rejection |
| `get_character_count_status()` | Character validation logic |

### Dependencies

The UI depends on existing, stable interfaces:
- **SocialMediaGenerator**: Core generation engine
- **Database**: PostgreSQL persistence layer
- **BrandVoice**: Brand guidelines management
- **PLATFORM_SPECS**: Platform configuration

### Session State

Streamlit's native session state manages:
```python
{
    'generated_posts': {
        'linkedin': { ... },
        'twitter': { ... },
        ...
    },
    'generator': SocialMediaGenerator(),
    'brand_voice': BrandVoice(),
    'generation_in_progress': bool
}
```

## Platform Specifications

| Platform | Char Limit | Image Size | Max Hashtags |
|----------|-----------|------------|--------------|
| LinkedIn | 3,000 | 1200×627 | 5 |
| Twitter | 280 | 1200×675 | 2 |
| Facebook | 63,206 | 1200×630 | 5 |
| Nextdoor | 5,000 | 1200×900 | 3 |

## Error Handling

The application gracefully handles:
- Empty or invalid prompts
- No platforms selected
- API failures during generation
- Character limit exceeded during editing
- Missing or failed image generation
- Database connection issues

## Development

### Adding New Platforms

1. Add platform spec to `src/core/config.py`
2. Add platform template to `src/core/prompt_templates.py`
3. UI automatically picks up new platforms from `PLATFORM_SPECS`

### Testing

```bash
# Run UI tests
pytest tests/test_streamlit_ui.py -v

# Test with coverage
pytest tests/test_streamlit_ui.py --cov=src.ui --cov-report=html
```

### Code Style

- **SOLID Principles**: Each function has one responsibility
- **KISS**: Simple, straightforward implementation
- **DRY**: Reuses existing services and configurations
- **Descriptive Names**: Functions clearly state their purpose
- **Docstrings**: All functions documented with purpose and parameters

## Troubleshooting

### Application Won't Start

```bash
# Check dependencies
pip list | grep streamlit

# Reinstall if needed
pip install streamlit

# Check environment variables
cat .env | grep -E "OPENAI|GOOGLE|DB"
```

### Images Not Displaying

- Verify `GOOGLE_API_KEY` in `.env`
- Check `generated_images/` directory exists
- Review logs for Gemini API errors
- Placeholder images created if generation fails

### Database Errors

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure `generated_posts` table exists (run `schema.sql`)

### Character Count Not Updating

- This is a known Streamlit behavior
- Press Enter or click outside text area to trigger update
- Count updates when switching tabs

## Future Enhancements (Out of Scope)

- Mobile responsiveness (desktop-only in current phase)
- Scheduled publishing (Phase 3)
- Analytics dashboard (separate module)
- Quality scoring automation (separate module)
- Batch generation
- Post history/archive view
- Performance analytics

## Related Documentation

- [Core Generator](../core/generator.py) - Post generation engine
- [Brand Voice](../../config/brand_guidelines.yaml) - Brand guidelines
- [Database Schema](../data/schema.sql) - Database structure
- [Platform Config](../core/config.py) - Platform specifications
