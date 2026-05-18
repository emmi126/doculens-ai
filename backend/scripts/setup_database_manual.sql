-- Manual Database Setup SQL
-- Run this as PostgreSQL superuser if the setup_database.sh script doesn't work
--
-- Usage:
--   sudo -u postgres psql -f setup_database_manual.sql

-- Configuration (change these if needed)
\set db_name 'doculens'
\set db_user 'doculens'
\set db_password '''password'''

-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'doculens') THEN
        CREATE USER doculens WITH PASSWORD 'password';
        RAISE NOTICE 'User "doculens" created';
    ELSE
        RAISE NOTICE 'User "doculens" already exists';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE doculens OWNER doculens'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'doculens')\gexec

-- Grant connection privilege
GRANT ALL PRIVILEGES ON DATABASE doculens TO doculens;

-- Connect to the database
\c doculens

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO doculens;
GRANT CREATE ON SCHEMA public TO doculens;
ALTER SCHEMA public OWNER TO doculens;

-- Grant default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO doculens;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO doculens;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO doculens;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Verify setup
\echo ''
\echo '=========================================='
\echo 'Database setup completed!'
\echo '=========================================='
\echo ''
\echo 'Database: doculens'
\echo 'User: doculens'
\echo 'Password: password'
\echo ''
\echo 'DATABASE_URL:'
\echo 'postgresql://doculens:password@localhost:5432/doculens'
\echo ''
\echo 'To verify, run:'
\echo '  psql -U doculens -d doculens'
\echo ''
