# Social Media Post Generator

> Multi-platform social media content generation using best-of-breed AI models

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

A production-ready system that generates platform-optimized social media posts with accompanying images, using **ChatGPT-4** for content generation and **Google Gemini** for image generation.

### Target Platforms
- 📘 **LinkedIn** - Professional networking
- 📘 **Facebook** - Community engagement
- 🐦 **Twitter/X** - Quick updates
- 🏘️ **Nextdoor** - Local community

### Key Features
- ✨ AI-powered content generation (GPT-4)
- 🎨 AI-generated images (Google Gemini)
- 🎯 Platform-specific optimization
- 📊 Quality checking and scoring
- 🤖 Automated publishing workflow
- 📈 Performance metrics tracking
- 🔄 Human-in-the-loop review

## Technology Stack

```
Frontend/Interface:    Streamlit (Phase 1) → React + FastAPI (Phase 2)
Orchestration:         LangChain + Python 3.10+
AI Models:             OpenAI GPT-4, Google Gemini Imagen
Database:              PostgreSQL
Storage:               AWS S3 / CloudFlare R2
Publishing APIs:       LinkedIn, Facebook, Twitter/X, Nextdoor
Scheduling:            APScheduler / Celery + Redis
Infrastructure:        Docker containers
```

## Project Structure

```
social-media-generator/
├── src/
│   ├── core/              # Core generation logic
│   │   ├── generator.py   # Main generator class
│   │   ├── config.py      # Configuration
│   │   └── prompt_templates.py
│   ├── data/              # Database interface
│   │   ├── database.py
│   │   └── schema.sql
│   ├── quality/           # Quality checking
│   │   └── checker.py
│   ├── automation/        # Auto-publish logic
│   │   └── decision_engine.py
│   ├── publishing/        # Platform publishers
│   │   ├── publisher.py
│   │   └── metrics_collector.py
│   └── ui/                # User interface
│       └── streamlit_app.py
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── config/                # Configuration files
├── generated_images/      # Generated images
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- OpenAI API key
- Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd social_media_agentic_solution
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

5. **Initialize database**
```bash
python scripts/setup_db.py
```

6. **Run tests**
```bash
pytest tests/ -v
```

7. **Start the UI**
```bash
streamlit run src/ui/streamlit_app.py
```

## Environment Variables

Copy [.env.example](.env.example) to `.env` and configure:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Google Gemini
GOOGLE_API_KEY=...

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_media_gen
DB_USER=postgres
DB_PASSWORD=...

# Platform APIs
LINKEDIN_ACCESS_TOKEN=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=social-media-images

# Jira Integration
JIRA_CLOUD_ID=f697d2b7-9442-444e-b462-e3a9b835734f
JIRA_PROJECT_KEY=SOC
```

## Usage

### Basic Usage

```python
from src.core.generator import SocialMediaGenerator

# Initialize generator
generator = SocialMediaGenerator()

# Generate a single post
post = generator.generate_post(
    user_prompt="Announcing our new AI-powered feature",
    platform="linkedin",
    context="Focus on productivity benefits",
    brand_voice="innovative and customer-focused"
)

print(post['content'])
print(f"Image: {post['image_path']}")
```

### Generate for All Platforms

```python
# Generate posts for all platforms at once
posts = generator.generate_all_platforms(
    user_prompt="Announcing our new AI-powered feature",
    context="Focus on productivity and efficiency",
    brand_voice="professional and engaging"
)

for platform, post_data in posts.items():
    print(f"\n{platform.upper()}:")
    print(post_data['content'])
```

### Using the Web Interface

1. Start Streamlit:
```bash
streamlit run src/ui/streamlit_app.py
```

2. Enter your post idea
3. Select target platforms
4. Review and edit generated content
5. Approve or regenerate
6. Schedule or publish

## Platform Specifications

| Platform | Char Limit | Optimal Length | Image Size | Hashtags |
|----------|-----------|----------------|------------|----------|
| LinkedIn | 3,000 | 150-300 words | 1200×627 | 3-5 |
| Twitter/X | 280 | 200-270 chars | 1200×675 | 1-2 |
| Facebook | 63,206 | 100-200 words | 1200×630 | 2-4 |
| Nextdoor | 5,000 | 100-250 words | 1200×900 | 1-2 |

## Development Phases

### ✅ Phase 1: Core Pipeline (Weeks 1-3)
- [x] Project setup and dependencies
- [x] Core generator class implementation
- [x] Platform-specific templates
- [x] OpenAI & Gemini integration
- [ ] CLI testing interface

### 🔄 Phase 2: Review Interface (Weeks 3-4)
- [ ] Streamlit web interface
- [ ] Post review and editing
- [ ] Approve/reject workflow
- [ ] Session state management

### ⏳ Phase 3: Database & Logging (Weeks 4-5)
- [x] Database schema
- [x] Database interface
- [ ] Migration scripts
- [ ] Analytics queries

### ⏳ Phase 4: Publishing Integration (Weeks 5-7)
- [ ] LinkedIn API integration
- [ ] Twitter/X API integration
- [ ] Facebook API integration
- [ ] Publishing orchestrator
- [ ] Scheduling system

### ⏳ Phase 5: Quality & Automation (Weeks 7-10)
- [ ] Quality checker implementation
- [ ] Automation decision engine
- [ ] Metrics collection system
- [ ] Confidence-based auto-publishing

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_generator.py -v

# Run with output
pytest -v -s
```

## Database Schema

The system uses PostgreSQL with the following main tables:

- **generated_posts** - All generated posts
- **post_feedback** - Human feedback and edits
- **performance_metrics** - Engagement data from platforms
- **quality_checks** - Quality check results
- **publishing_log** - Publishing attempts and results

See [src/data/schema.sql](src/data/schema.sql) for complete schema.

## API Rate Limits

| Platform | Rate Limit |
|----------|-----------|
| LinkedIn | 100 posts/day per person |
| Twitter/X | 300 posts/3 hours |
| Facebook | Varies by page |
| Nextdoor | No public API (manual) |

## Cost Estimates

Monthly operating costs for 4 posts/day (120 posts/month):

| Item | Cost |
|------|------|
| OpenAI GPT-4 | ~$15 |
| Google Gemini | ~$20 |
| Database (PostgreSQL) | $15-25 |
| Storage (S3/R2) | $5-10 |
| Hosting | $20-50 |
| **Total** | **$75-120/month** |

## Jira Integration

This project is tracked in Jira:
- **Project Key:** SOC
- **Epic:** SOC-1 - Social Media Post Generator
- **Cloud ID:** f697d2b7-9442-444e-b462-e3a9b835734f

View all tasks at: [Jira Board](https://christianfitzgibbonpersonal.atlassian.net/jira/software/projects/SOC)

## Contributing

1. Check [Jira board](https://christianfitzgibbonpersonal.atlassian.net/jira/software/projects/SOC) for available tasks
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Check connection
psql -h localhost -U postgres -d social_media_gen
```

### API Key Issues
```bash
# Verify environment variables are loaded
python -c "from src.core.config import Config; print(Config.validate())"
```

### Image Generation Issues
- Ensure `generated_images/` directory exists
- Check Google Gemini API quota
- Verify image dimensions are correct

## Documentation

- [Project Specification](social-media-generator-project-spec.md) - Complete project spec
- [Atlassian MCP](Atlassian_MCP.md) - Jira integration details
- [Brand Guidelines](config/brand_guidelines.yaml) - Brand voice configuration

## Roadmap

- [ ] Complete Phase 1-5 implementation
- [ ] Add analytics dashboard (React)
- [ ] Implement learning from feedback
- [ ] Add multi-account support
- [ ] Build content calendar
- [ ] Add video support
- [ ] Competitor analysis features

## License

MIT License - see LICENSE file for details

## Contact

**Project Lead:** Christian Fitz-Gibbon
**Start Date:** January 7, 2026
**Repository:** social_media_agentic_solution
**Jira Project:** SOC - Social Media Posts

## Acknowledgments

- OpenAI GPT-4 for content generation
- Google Gemini for image generation
- LangChain for AI orchestration
- Streamlit for rapid UI development

---

**Built with ❤️ using Claude Code and best-of-breed AI models**
