-- Rollback Migration: 001_initial_schema
-- Description: Drop all tables created in initial schema
-- Date: 2025-01-17

-- WARNING: This will delete all data!

-- Drop triggers
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
DROP TRIGGER IF EXISTS update_courses_updated_at ON courses;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables (in reverse order of creation due to foreign keys)
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Note: Extensions are not dropped to avoid affecting other databases

-- Completion message
DO $$
BEGIN
    RAISE NOTICE 'Rollback of migration 001_initial_schema completed!';
    RAISE NOTICE 'All tables have been dropped.';
END $$;
