#!/usr/bin/env bash
#
# Database backup script for the social media generator.
# Creates a timestamped pg_dump backup of the social_media_gen database.
#
# Usage:
#   ./scripts/backup_db.sh
#   ./scripts/backup_db.sh /custom/backup/dir
#
# Environment variables (from .env or shell):
#   DB_HOST     - Database host (default: localhost)
#   DB_PORT     - Database port (default: 5432)
#   DB_NAME     - Database name (default: social_media_gen)
#   DB_USER     - Database user (default: postgres)
#   DB_PASSWORD - Database password (required, set via PGPASSWORD)

set -euo pipefail

# Load .env file if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Configuration with defaults
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-social_media_gen}"
DB_USER="${DB_USER:-postgres}"

# Backup directory (argument or default)
BACKUP_DIR="${1:-$PROJECT_ROOT/backups}"
mkdir -p "$BACKUP_DIR"

# Timestamp for filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

echo "============================================"
echo "Social Media Generator - Database Backup"
echo "============================================"
echo ""
echo "Database: $DB_NAME@$DB_HOST:$DB_PORT"
echo "Backup to: $BACKUP_FILE"
echo ""

# Check if pg_dump is available
if ! command -v pg_dump &> /dev/null; then
    echo "Error: pg_dump not found. Please install PostgreSQL client tools."
    exit 1
fi

# Check password
if [ -z "${DB_PASSWORD:-}" ]; then
    echo "Error: DB_PASSWORD not set. Set it in .env or export it."
    exit 1
fi

# Run backup
export PGPASSWORD="$DB_PASSWORD"
pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-privileges \
    -f "$BACKUP_FILE"

unset PGPASSWORD

# Report
BACKUP_SIZE=$(wc -c < "$BACKUP_FILE" | tr -d ' ')
echo "Backup complete: $BACKUP_FILE ($BACKUP_SIZE bytes)"

# Clean up old backups (keep last 10)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/${DB_NAME}_*.sql 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 10 ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - 10))
    echo "Cleaning up $REMOVE_COUNT old backup(s)..."
    ls -1t "$BACKUP_DIR"/${DB_NAME}_*.sql | tail -n "$REMOVE_COUNT" | xargs rm -f
fi

echo ""
echo "Done."
