#!/usr/bin/env python3
"""
Database setup script.
Initializes the PostgreSQL database and creates all tables.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import Config  # noqa: E402


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = conn.cursor()

        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.DB_NAME,))

        if not cur.fetchone():
            print(f"Creating database '{Config.DB_NAME}'...")
            cur.execute(f"CREATE DATABASE {Config.DB_NAME}")
            print(f"✓ Database '{Config.DB_NAME}' created successfully")
        else:
            print(f"Database '{Config.DB_NAME}' already exists")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)


def create_tables():
    """Create all tables using schema.sql"""
    try:
        # Connect to the target database
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
        )

        cur = conn.cursor()

        # Read schema file
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "migrations", "001_initial_schema.sql"
        )

        print(f"\nReading schema from: {schema_path}")

        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Execute schema
        print("Creating tables...")
        cur.execute(schema_sql)
        conn.commit()

        print("✓ All tables created successfully")

        # Verify tables
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )

        tables = cur.fetchall()
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)


def main():
    """Main setup function"""
    print("=" * 60)
    print("Social Media Generator - Database Setup")
    print("=" * 60)

    print("\nDatabase Configuration:")
    print(f"  Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"  Database: {Config.DB_NAME}")
    print(f"  User: {Config.DB_USER}")

    # Validate configuration
    if not Config.DB_PASSWORD:
        print("\n❌ Error: DB_PASSWORD not set in environment")
        print("Please set DB_PASSWORD in your .env file")
        sys.exit(1)

    # Create database
    create_database()

    # Create tables
    create_tables()

    print("\n" + "=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
