# Phase 4 RAG Implementation

Phase 4 added retrieval-augmented note processing and related-note discovery.

## Architecture

1. OCR extracts text from an uploaded image.
2. The embedding service converts the OCR text into a 384-dimensional vector.
3. PostgreSQL and pgvector retrieve similar active documents from the same course.
4. Relevant historical notes are supplied to Claude as optional context.
5. Claude formats the new note as Markdown.
6. The formatted note receives its own embedding and is persisted.

## Main Components

- `services/embedding_service.py`: sentence-transformer loading, chunking, and vector creation
- `services/vector_store.py`: pgvector similarity queries and related-note retrieval
- `services/llm_service.py`: basic and RAG-enhanced Markdown formatting
- `routes/documents.py`: document CRUD and related-note endpoint
- `main.py`: upload, OCR, formatting, retrieval, and persistence workflow

## Retrieval Constraints

- Searches are restricted to the current course.
- Only active documents with embeddings are considered.
- The current document is excluded from related-note results.
- Similarity thresholds reduce irrelevant context.

## Operational Notes

- The embedding model is `paraphrase-multilingual-MiniLM-L12-v2`.
- Initial model loading can take several seconds.
- Historical note content is truncated before it is added to prompts.
- Vector-store failures currently return empty results and are logged.

This document summarizes the implemented system. Current source code is authoritative where behavior differs.
