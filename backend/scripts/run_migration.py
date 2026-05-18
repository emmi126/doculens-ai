#!/usr/bin/env python3
"""
Database Migration Runner

This script runs SQL migration files against the PostgreSQL database.

Usage:
    python run_migration.py migrations/001_initial_schema.sql
    python run_migration.py migrations/001_initial_schema_rollback.sql
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection from DATABASE_URL environment variable"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable not set. "
            "Please check your .env file."
        )

    print(f"Connecting to database...")
    return psycopg2.connect(database_url)


def run_migration_file(filepath: str):
    """Run a SQL migration file"""
    filepath = Path(filepath)

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    print(f"\nRunning migration: {filepath.name}")
    print("=" * 60)

    # Read SQL file
    with open(filepath, 'r') as f:
        sql_content = f.read()

    # Connect to database and execute
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = True  # For DDL statements

        with conn.cursor() as cursor:
            # Execute the SQL
            cursor.execute(sql_content)

            # Print any notices (like our completion messages)
            for notice in conn.notices:
                print(notice.strip())

        print("=" * 60)
        print(f"✓ Migration completed successfully: {filepath.name}")

    except psycopg2.Error as e:
        print(f"\n✗ Migration failed!")
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        if conn:
            conn.close()


def list_tables():
    """List all tables in the database"""
    conn = None
    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = cursor.fetchall()

            print("\nCurrent tables in database:")
            print("-" * 40)
            if tables:
                for table in tables:
                    print(f"  • {table[0]}")
            else:
                print("  (no tables)")
            print()

    except psycopg2.Error as e:
        print(f"Error listing tables: {e}")

    finally:
        if conn:
            conn.close()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file.sql>")
        print("\nAvailable migrations:")
        migrations_dir = Path(__file__).parent / "migrations"
        if migrations_dir.exists():
            for sql_file in sorted(migrations_dir.glob("*.sql")):
                print(f"  • {sql_file.relative_to(Path(__file__).parent)}")
        sys.exit(1)

    migration_file = sys.argv[1]

    # Show current state
    print("\n" + "=" * 60)
    print("Database Migration Tool")
    print("=" * 60)

    # Run migration
    run_migration_file(migration_file)

    # Show final state
    list_tables()


if __name__ == "__main__":
    main()
