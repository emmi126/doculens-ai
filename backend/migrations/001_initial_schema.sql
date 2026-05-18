-- Migration: 001_initial_schema
-- Description: Create initial database schema for DocuLens
-- Date: 2025-01-17

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(512),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_auth0_user_id ON users(auth0_user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- Add comments
COMMENT ON TABLE users IS 'User accounts synced from Auth0';
COMMENT ON COLUMN users.auth0_user_id IS 'Auth0 user identifier from JWT sub claim';
COMMENT ON COLUMN users.email_verified IS 'Email verification status from Auth0';

-- ============================================
-- COURSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    icon VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'trash')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Courses indexes
CREATE INDEX IF NOT EXISTS idx_courses_user_id ON courses(user_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_courses_user_status ON courses(user_id, status);

-- Add comments
COMMENT ON TABLE courses IS 'Course organization for grouping documents';
COMMENT ON COLUMN courses.color IS 'Hex color code for UI customization (#RRGGBB)';
COMMENT ON COLUMN courses.icon IS 'Emoji or icon identifier for visual distinction';
COMMENT ON COLUMN courses.status IS 'active or trash (soft delete)';

-- ============================================
-- DOCUMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    original_text TEXT NOT NULL,
    formatted_note TEXT NOT NULL,
    excerpt VARCHAR(200),
    image_path VARCHAR(512),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'trash')),
    processing_time REAL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_course_id ON documents(course_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_course_status ON documents(course_id, status);
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING gin (metadata);

-- Full-text search indexes (requires pg_trgm extension)
-- Uncomment these if you want full-text search capabilities
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_documents_title_trgm ON documents USING gin (title gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS idx_documents_formatted_note_trgm ON documents USING gin (formatted_note gin_trgm_ops);

-- Add comments
COMMENT ON TABLE documents IS 'Processed note documents';
COMMENT ON COLUMN documents.original_text IS 'Raw OCR extracted text';
COMMENT ON COLUMN documents.formatted_note IS 'LLM formatted markdown content';
COMMENT ON COLUMN documents.excerpt IS 'First 200 characters for preview';
COMMENT ON COLUMN documents.processing_time IS 'Time taken for OCR + LLM processing (seconds)';
COMMENT ON COLUMN documents.metadata IS 'JSONB field for flexible data storage (OCR confidence, context, etc.)';

-- ============================================
-- TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for courses table
DROP TRIGGER IF EXISTS update_courses_updated_at ON courses;
CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for documents table
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMPLETION
-- ============================================

-- Verify tables were created
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema completed successfully!';
    RAISE NOTICE 'Tables created: users, courses, documents';
    RAISE NOTICE 'Total indexes: %', (SELECT count(*) FROM pg_indexes WHERE schemaname = 'public');
END $$;
