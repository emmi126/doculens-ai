-- Migration: Add vector embeddings for RAG functionality
-- Date: 2025-12-06
-- Description: Adds pgvector extension and embedding column to documents table

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to documents table
ALTER TABLE documents
ADD COLUMN embedding vector(384);

-- Create index for vector similarity search using HNSW
-- This significantly speeds up nearest neighbor queries
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents
USING hnsw (embedding vector_cosine_ops);

-- Add comment to explain the column
COMMENT ON COLUMN documents.embedding IS 'Vector embedding (384 dimensions) for semantic similarity search using sentence-transformers';

-- Verify the change
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'documents'
AND column_name = 'embedding';
