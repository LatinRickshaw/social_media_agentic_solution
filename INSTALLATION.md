# Installation Notes

## Setup Complete ✅

The project setup for SOC-2 has been completed with the following components:

### ✅ Completed Tasks

1. **Project Directory Structure** - All directories and `__init__.py` files created
2. **Configuration Files** - `.env.example`, `requirements.txt`, `.gitignore` created
3. **Virtual Environment** - Created at `./venv/`
4. **Core Dependencies Installed** - Development tools installed
5. **Pre-commit Hooks** - Configured and installed

### 📦 Installed Packages

The following core packages have been successfully installed:

```
python-dotenv==1.2.1      # Environment variable management
requests==2.32.5          # HTTP library
pydantic==2.12.5          # Data validation
pytest==9.0.2             # Testing framework
black==25.12.0            # Code formatter
flake8==7.3.0             # Linter
mypy==1.19.1              # Type checker
pre-commit==4.5.1         # Git hooks
```

### ⚠️ Additional Dependencies Required

Some packages require system-level dependencies or have compatibility issues with Python 3.13:

**Database Packages:**
- `psycopg2-binary` - Requires PostgreSQL development libraries
- `sqlalchemy` - Database ORM

**AI/ML Packages:**
- `langchain` - LangChain framework
- `openai` - OpenAI API client
- `google-generativeai` - Google Gemini API

**UI Packages:**
- `streamlit` - Web UI framework
- `pillow` - Image processing

**Social Media APIs:**
- `tweepy` - Twitter API
- `python-linkedin-v2` - LinkedIn API
- `facebook-sdk` - Facebook API

**Scheduling:**
- `apscheduler` - Task scheduling
- `celery` - Distributed task queue
- `redis` - Redis client

## How to Install Remaining Packages

### Option 1: Install as Needed (Recommended)

Install packages when you need them for specific phases:

```bash
# Activate virtual environment
source venv/bin/activate

# Phase 1: Core AI packages
pip install langchain openai google-generativeai

# Phase 2: UI
pip install streamlit pillow

# Phase 3: Database (requires PostgreSQL installed)
pip install psycopg2-binary sqlalchemy

# Phase 4: Social Media APIs
pip install tweepy python-linkedin-v2 facebook-sdk

# Phase 5: Scheduling
pip install apscheduler celery redis
```

### Option 2: Install PostgreSQL First

If you need database functionality:

```bash
# macOS (using Homebrew)
brew install postgresql@15

# Then install Python database packages
source venv/bin/activate
pip install psycopg2-binary sqlalchemy
```

### Option 3: Use Docker

Use Docker to avoid system dependency issues:

```bash
# Will be created in Phase 6
docker-compose up -d
```

## Pre-commit Hooks

Pre-commit hooks are configured and installed. They will run automatically before each commit to:

- Format code with Black
- Lint code with Flake8
- Type check with MyPy
- Check YAML, JSON, TOML files
- Remove trailing whitespace
- Fix end-of-file issues

Run manually:
```bash
pre-commit run --all-files
```

## Verification

To verify your setup:

```bash
# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list

# Check pre-commit
pre-commit --version

# Run tests (when available)
pytest tests/ -v
```

## Configuration

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required for Phase 1
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Required for Phase 3
DB_PASSWORD=...

# Required for Phase 4
LINKEDIN_ACCESS_TOKEN=...
FACEBOOK_ACCESS_TOKEN=...
TWITTER_API_KEY=...
# ... etc
```

## Next Steps

1. **SOC-3**: Core Generator Class Implementation
   - Install AI packages: `pip install langchain openai google-generativeai`
   - Implement generator functionality
   - Test with CLI

2. **SOC-4**: Platform-Specific Templates
   - Refine prompt templates
   - Test generation for each platform

3. **SOC-5**: Streamlit UI
   - Install: `pip install streamlit pillow`
   - Build review interface

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Package Installation Errors

```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Install packages one by one
pip install package-name
```

### Pre-commit Hook Issues

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks
pre-commit autoupdate
```

## Development Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# ... edit files ...

# 4. Run pre-commit checks
pre-commit run --all-files

# 5. Run tests
pytest tests/ -v

# 6. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: your feature description"

# 7. Push
git push origin feature/your-feature
```

## Project Status

- ✅ **SOC-2**: Project Setup & Dependencies (COMPLETE)
- 🔄 **SOC-3**: Core Generator (READY TO START)
- ⏳ **SOC-4**: Platform Templates (READY TO START)
- ⏳ **SOC-5+**: Future phases

---

**Setup completed:** January 7, 2026
**Next task:** SOC-3 - Core Generator Class Implementation
