# Installation Guide

## Prerequisites

- Python 3.10+ (tested on 3.13)
- PostgreSQL 12+
- OpenAI API key
- Google Gemini API key

## Quick Setup

### 1. Clone and create virtual environment

```bash
git clone <repository-url>
cd social_media_agentic_solution
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 4. Initialize database

```bash
python scripts/setup_db.py
```

### 5. Run tests

```bash
pytest tests/ -v
```

### 6. Start the app

```bash
streamlit run src/ui/streamlit_app.py
```

## Docker Setup (Alternative)

See the Docker section in [README.md](README.md#docker) for running the full stack with Docker Compose.

## Pre-commit Hooks

Pre-commit hooks are configured to run automatically on each commit:

- Code formatting (Black)
- Linting (Flake8)
- Type checking (MyPy)
- YAML/JSON validation
- Trailing whitespace removal

Run manually:

```bash
pre-commit run --all-files
```

## Troubleshooting

### Virtual Environment Issues

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Package Installation Errors

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### PostgreSQL Not Found

```bash
# macOS (Homebrew)
brew install postgresql@15

# Or use Docker:
docker compose up db
```

## Project Status

- **SOC-2**: Project Setup & Dependencies — Done
- **SOC-3**: Core Generator — Done
- **SOC-4**: Platform Templates — Done
- **SOC-5**: Streamlit Review Interface — Done
- **SOC-6**: Database Setup & Migrations — Done
- **SOC-7+**: Publishing, Quality, Automation — Planned

---

**Setup originally completed:** January 7, 2026
