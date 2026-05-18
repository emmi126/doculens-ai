#!/bin/bash
# Database Setup Script for DocuLens
# This script creates the database and sets up proper permissions

set -e  # Exit on error

echo "=========================================="
echo "DocuLens Database Setup"
echo "=========================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL first:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  macOS: brew install postgresql"
    exit 1
fi

# Configuration
DB_NAME="${DB_NAME:-doculens}"
DB_USER="${DB_USER:-doculens}"
DB_PASSWORD="${DB_PASSWORD:-password}"

echo "Database Configuration:"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""

# Prompt for confirmation
read -p "Continue with these settings? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Creating database and user..."
echo ""

# Run SQL commands as postgres superuser
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant connection privilege
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to the database
\c $DB_NAME

-- Grant schema permissions (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT CREATE ON SCHEMA public TO $DB_USER;
ALTER SCHEMA public OWNER TO $DB_USER;

-- Grant default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Summary
\echo ''
\echo '=========================================='
\echo 'Database setup completed successfully!'
\echo '=========================================='
\echo ''
\echo 'Connection details:'
\echo '  Host: localhost'
\echo '  Port: 5432'
\echo '  Database: $DB_NAME'
\echo '  User: $DB_USER'
\echo '  Password: $DB_PASSWORD'
\echo ''
\echo 'DATABASE_URL:'
\echo 'postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME'
\echo ''
EOF

echo ""
echo "✓ Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update your .env file with the DATABASE_URL shown above"
echo "  2. Run the migration: python run_migration.py migrations/001_initial_schema.sql"
echo ""
