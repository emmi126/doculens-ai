# Database Integration Report

This archival report records the Phase 4 database integration work for DocuLens AI.

## Implemented

- PostgreSQL persistence for users, courses, and documents
- UUID primary keys and ownership relationships
- Soft deletion for courses and documents
- JSONB document metadata
- The `pgcrypto` extension for UUID support
- The `vector` extension and a 384-dimensional document embedding column
- An HNSW cosine-similarity index
- Course-scoped semantic retrieval
- Automatic embedding generation when documents are created or updated

## Migrations

The database is defined by:

- `migrations/001_initial_schema.sql`
- `migrations/002_add_vector_embeddings.sql`

Apply both migrations in order with `scripts/run_migration.py`.

## Current Validation

The local development database has the required `users`, `courses`, and `documents` tables. The `pgcrypto` and `vector` extensions and the `documents.embedding` column have also been verified.

This report is retained as historical implementation documentation. The root README and current source code are authoritative for setup and behavior.
