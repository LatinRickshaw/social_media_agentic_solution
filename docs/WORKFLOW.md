# Development Workflow

This document describes the standard development workflow for the Social Media Post Generator project.

## Overview

Every task follows a consistent workflow that ensures proper tracking, documentation, and integration:

1. **Start** with a Jira ticket
2. **Develop** the feature or fix
3. **Complete** using the automated workflow
4. **Verify** in Jira and Git

## Standard Workflow

### 1. Pick a Task from Jira

Visit the [Jira board](https://christianfitzgibbonpersonal.atlassian.net/jira/software/projects/SOC) and select a task.

```bash
# Example tasks:
# SOC-5: Phase 2.1: Streamlit Review Interface
# SOC-8: Phase 4.1: LinkedIn API Integration
# SOC-12: Phase 5.1: Quality Checker Implementation
```

### 2. Transition to "In Progress"

Move the ticket to "In Progress" in Jira when you start working.

### 3. Develop the Feature

Write code, tests, and documentation following project standards:

```bash
# Run tests frequently
pytest tests/ -v

# Check code formatting
black src/
flake8 src/

# Ensure pre-commit hooks pass
pre-commit run --all-files
```

### 4. Complete the Task (Automated)

When your work is done, use the `/complete-task` skill:

```bash
/complete-task SOC-5 "Implemented Streamlit review interface with post preview and approval workflow"
```

This single command will:
1. ✅ Update the Jira ticket with work summary
2. ✅ Transition the Jira ticket to "Done"
3. ✅ Generate a descriptive commit message
4. ✅ Commit changes to Git
5. ✅ Push to remote repository

### 5. Verify

Check that everything completed successfully:

- **Jira**: Ticket is in "Done" status with comment
- **Git**: Commit appears in `git log` with proper message
- **Remote**: Changes are pushed to GitHub/GitLab

## Commit Message Format

All commits follow this format:

```
[JIRA-KEY] Brief one-line description

Detailed changes:
- Implemented feature X with Y
- Added tests for Z
- Updated documentation for A

Jira: https://christianfitzgibbonpersonal.atlassian.net/browse/JIRA-KEY

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Example:

```
[SOC-5] Implement Streamlit review interface

Detailed changes:
- Created streamlit_app.py with post preview and editing
- Added approval workflow with feedback collection
- Implemented platform-specific preview formatting
- Added tests for UI components

Jira: https://christianfitzgibbonpersonal.atlassian.net/browse/SOC-5

🤖 Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Jira Update Format

The Jira ticket will receive a comment like:

```markdown
Work completed:

Implemented Streamlit review interface with post preview and approval workflow

Files changed:
- src/ui/streamlit_app.py (new)
- tests/test_ui.py (new)
- requirements.txt (modified)
- README.md (modified)

Committed and pushed to repository.
```

## Manual Workflow (Fallback)

If you need to complete a task manually without the skill:

### 1. Check Git Status

```bash
git status
git diff
```

### 2. Update Jira

Go to the Jira ticket and:
- Add a comment summarizing the work
- Transition to "Done"

### 3. Commit Changes

```bash
git add .
git commit -m "[SOC-5] Implement Streamlit review interface

Detailed changes:
- Created streamlit_app.py
- Added tests
- Updated docs

Jira: https://christianfitzgibbonpersonal.atlassian.net/browse/SOC-5"
```

### 4. Push to Remote

```bash
git push origin main
```

## Best Practices

### Before Starting a Task

- ✅ Pull latest changes: `git pull`
- ✅ Ensure virtual environment is active: `source venv/bin/activate`
- ✅ Verify dependencies are up to date: `pip install -r requirements.txt`
- ✅ Check Jira ticket for acceptance criteria

### During Development

- ✅ Commit frequently with descriptive messages
- ✅ Run tests before committing: `pytest tests/ -v`
- ✅ Keep Jira ticket updated with progress notes
- ✅ Follow code style guidelines (Black, Flake8)

### Before Completing a Task

- ✅ All tests pass: `pytest tests/ -v --cov=src`
- ✅ Code is formatted: `black src/ tests/`
- ✅ No linting errors: `flake8 src/ tests/`
- ✅ Documentation is updated
- ✅ Environment variables are documented in [.env.example](.env.example)
- ✅ README is updated if needed

### After Completing a Task

- ✅ Verify Jira ticket is in "Done" status
- ✅ Verify commit appears in remote repository
- ✅ Update [PROJECT_SETUP_SUMMARY.md](PROJECT_SETUP_SUMMARY.md) if major milestone
- ✅ Notify team members if relevant

## Task Dependencies

Some tasks depend on others. Check the Jira board for dependencies:

```
Phase 1: Foundation
├── SOC-2: Project Setup ✅
├── SOC-3: Core Generator ✅
└── SOC-4: Platform Templates ✅

Phase 2: User Interface
└── SOC-5: Streamlit UI (requires Phase 1)

Phase 3: Data Layer
├── SOC-6: Database Setup (requires Phase 1)
└── SOC-7: Database Interface (requires SOC-6)

Phase 4: Publishing
├── SOC-8: LinkedIn API (requires Phase 2, 3)
├── SOC-9: Twitter API (requires Phase 2, 3)
├── SOC-10: Facebook API (requires Phase 2, 3)
└── SOC-11: Publishing Orchestrator (requires SOC-8, 9, 10)

Phase 5: Automation
├── SOC-12: Quality Checker (requires Phase 4)
├── SOC-13: Automation Engine (requires SOC-12)
└── SOC-14: Metrics Collection (requires Phase 4)
```

## Branching Strategy

Currently using a simple workflow:

```
main (production-ready code)
```

For future feature branches:

```bash
# Create feature branch
git checkout -b feature/SOC-5-streamlit-ui

# Work on feature
git commit -m "[SOC-5] Add initial UI structure"

# Push feature branch
git push origin feature/SOC-5-streamlit-ui

# Create PR when ready
# Merge to main after review
```

## Quick Reference

### Common Commands

```bash
# Activate environment
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Run pre-commit checks
pre-commit run --all-files

# Complete a task (automated)
/complete-task SOC-5 "Description of work"

# Check git status
git status
git log --oneline -5
```

### File Locations

- **Source code**: [src/](src/)
- **Tests**: [tests/](tests/)
- **Configuration**: [config/](config/)
- **Database scripts**: [scripts/](scripts/)
- **Documentation**: [README.md](README.md), [PROJECT_SETUP_SUMMARY.md](PROJECT_SETUP_SUMMARY.md)
- **Environment variables**: [.env.example](.env.example)

### Important Links

- **Jira Board**: https://christianfitzgibbonpersonal.atlassian.net/jira/software/projects/SOC
- **Epic**: SOC-1 - Social Media Post Generator
- **Project Spec**: [social-media-generator-project-spec.md](social-media-generator-project-spec.md)

## Troubleshooting

### Skill Not Working

If `/complete-task` doesn't work:

1. Check that [.mcp.json](.mcp.json) has Atlassian MCP configured
2. Verify you have permissions to update Jira tickets
3. Ensure git remote is configured: `git remote -v`
4. Fall back to manual workflow (see above)

### Git Push Fails

```bash
# Pull latest changes first
git pull --rebase origin main

# Resolve conflicts if any
git status
# Fix conflicts, then:
git add .
git rebase --continue

# Push again
git push origin main
```

### Jira Transition Fails

- Check ticket is in correct status for transition
- Verify you have permissions to transition
- Check Jira workflow for valid transitions

### Tests Failing

```bash
# Run specific test
pytest tests/test_generator.py::test_specific_function -v

# Run with print output
pytest tests/ -v -s

# Skip slow tests
pytest tests/ -v -m "not slow"
```

## Getting Help

- **Claude Code**: Type your question or use `/help`
- **Project Issues**: Create issue in repository
- **Jira**: Add comments to tickets with questions
- **Documentation**: Check [README.md](README.md) and [PROJECT_SETUP_SUMMARY.md](PROJECT_SETUP_SUMMARY.md)

---

**Remember**: The workflow is designed to be simple and consistent. Every task follows the same pattern: Pick → Develop → Complete → Verify. Use `/complete-task` to automate the completion steps and maintain consistency across the project.
