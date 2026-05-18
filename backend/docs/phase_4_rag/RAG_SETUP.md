# RAG System Setup Guide

## Phase 4: Vector Database and Embedding Setup

This guide covers the setup process for the RAG (Retrieval-Augmented Generation) system in DocuLens.

## Prerequisites

1. PostgreSQL 12+ installed
2. Superuser access to PostgreSQL database

## Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `pgvector==0.2.4` - PostgreSQL vector extension Python adapter
- `sentence-transformers==2.2.2` - For generating embeddings
- `torch==2.1.0` - Required by sentence-transformers

## Step 2: Enable pgvector Extension in PostgreSQL

### Option A: Using psql Command Line

```bash
# Connect to your database
psql -U your_username -d doculens

# Run the setup script
\i backend/scripts/setup_pgvector.sql
```

### Option B: Direct SQL

```sql
-- Connect to your database and run:
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation:
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

Expected output:
```
 extname | extversion
---------+------------
 vector  | 0.5.0
```

## Step 3: Run Database Migration

After enabling the pgvector extension, run the Alembic migration to add the embedding column:

```bash
cd backend
alembic upgrade head
```

This will add a `embedding` column of type `vector(384)` to the `documents` table.

## Step 4: Index Existing Notes (If Applicable)

If you have existing notes in the database, run the indexing script:

```bash
cd backend
python scripts/index_existing_notes.py
```

This will:
- Load all existing documents
- Generate embeddings for each document
- Update the database with the embeddings

## Architecture Overview

### Embedding Model

- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions**: 384
- **Languages**: Supports 50+ languages including English and Chinese
- **Size**: ~50MB
- **Speed**: ~100ms per document on CPU

### Vector Search

- **Method**: Cosine similarity search
- **Index**: HNSW (Hierarchical Navigable Small World) for fast retrieval
- **Scope**: Course-level isolation (only searches within the same course)

### RAG Flow

1. User uploads new note image
2. OCR extracts text from image
3. System generates embedding for the new text
4. Vector search finds top-3 similar historical notes in the same course
5. Retrieved context + new OCR text sent to Claude
6. Claude generates integrated, contextualized note

## Troubleshooting

### Error: "extension 'vector' does not exist"

**Solution**: You need superuser privileges to install extensions.

```bash
# If using local PostgreSQL
sudo -u postgres psql doculens -c "CREATE EXTENSION vector;"

# If using Docker
docker exec -it your_postgres_container psql -U postgres -d doculens -c "CREATE EXTENSION vector;"
```

### Error: "could not open extension control file"

**Solution**: Install the pgvector extension on your PostgreSQL server.

**macOS (Homebrew)**:
```bash
brew install pgvector
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql-14-pgvector
```

**From source**:
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Error: Torch installation fails

**Solution**: Install CPU-only version of PyTorch (lighter weight):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Testing the Setup

After completing all steps, verify the setup:

```python
# Test script
python scripts/test_rag_setup.py
```

Expected output:
```
✓ pgvector extension enabled
✓ Embedding model loaded successfully
✓ Vector search working
✓ RAG pipeline functional
```

## Performance Notes

- **Embedding generation**: ~100-200ms per document (CPU)
- **Vector search**: <10ms for databases with <10,000 documents
- **Memory usage**: ~200MB for the embedding model (stays in memory)
- **Storage**: ~1.5KB per document (384 floats × 4 bytes)

## Next Steps

After setup is complete:
1. Test with a multi-lecture course scenario
2. Adjust retrieval parameters (top-k, similarity threshold) if needed
3. Implement frontend display for related notes
