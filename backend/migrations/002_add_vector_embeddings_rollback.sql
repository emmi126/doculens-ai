-- Rollback: Remove vector embeddings
-- Date: 2025-12-06
-- Description: Removes embedding column and pgvector extension

-- Drop the HNSW index
DROP INDEX IF EXISTS documents_embedding_idx;

-- Remove embedding column from documents table
ALTER TABLE documents
DROP COLUMN IF EXISTS embedding;

-- Note: We do NOT drop the vector extension as it might be used by other tables
-- If you want to completely remove pgvector, manually run:
-- DROP EXTENSION IF EXISTS vector CASCADE;

-- Verify the change
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'documents'
ORDER BY ordinal_position;
