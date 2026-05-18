-- Setup script for enabling pgvector extension in PostgreSQL
-- Run this script as a PostgreSQL superuser before running migrations

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Show available vector operations
\dx+ vector
