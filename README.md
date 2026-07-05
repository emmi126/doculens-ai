# DocuLens AI

DocuLens AI turns photos, handwritten notes, whiteboards, and slide screenshots into clean Markdown notes.

## Overview

The app has a Next.js frontend, a FastAPI backend, PostgreSQL storage, and pgvector-based semantic search. OCR is handled by Google Cloud Vision, and note formatting is handled by Anthropic Claude.

## Features

- Upload note images and process them into structured Markdown
- Organize notes by course
- Edit processed notes in a Markdown editor
- Store notes in PostgreSQL
- Generate embeddings for related-note search with pgvector
- Use Auth0 for real user authentication

## Requirements

- Python 3.12+
- Node.js 20+
- PostgreSQL 14+ with pgvector
- Google Cloud project with the Vision API enabled
- Anthropic API key

## Backend Setup

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Authenticate Google Cloud locally with Application Default Credentials:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://doculens:password@localhost:5432/doculens
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-6
DOCULENS_DEBUG=true
ENABLE_DEMO_AI_FALLBACK=false
```

For deployed environments, configure Google credentials through the hosting platform's service identity rather than a local ADC login.

Create the PostgreSQL database configured by `DATABASE_URL`, then apply the migrations. The database user must be allowed to enable the `pgcrypto` and `vector` extensions.

```bash
python scripts/run_migration.py migrations/001_initial_schema.sql
python scripts/run_migration.py migrations/002_add_vector_embeddings.sql
```

Start the backend:

```bash
python main.py
```

Backend URL: `http://localhost:8000`

## Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

Frontend URL: `http://localhost:3000`

## Useful API Endpoints

- `GET /health`
- `POST /process-note`
- `GET /api/courses/`
- `POST /api/courses/`
- `GET /api/documents/courses/{course_id}/documents`
- `GET /api/documents/{document_id}`
- `PUT /api/documents/{document_id}`
- `DELETE /api/documents/{document_id}`
