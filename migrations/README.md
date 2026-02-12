# Database Migrations

Simple numbered SQL migration scripts for the social media generator database.

## Convention

- Files are named `NNN_description.sql` (e.g., `001_initial_schema.sql`)
- Each migration is idempotent where possible (`CREATE IF NOT EXISTS`, `DROP IF EXISTS`)
- Migrations are applied in order

## Applying Migrations

```bash
# Apply a specific migration
psql -d social_media_gen -f migrations/001_initial_schema.sql

# Or use the setup script for initial setup
python scripts/setup_db.py
```

## Current Migrations

| Migration | Description | Date |
|-----------|-------------|------|
| 001 | Initial schema (5 tables, indexes, trigger) | 2026-02-12 |
