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
- Node.js 18+
- PostgreSQL 14+ with pgvector
- Google Cloud Vision credentials
- Anthropic API key
- Auth0 application/API configuration

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://doculens:password@localhost:5432/doculens
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
ANTHROPIC_API_KEY=your_anthropic_key
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_AUDIENCE=your-api-audience
ENABLE_DEMO_AI_FALLBACK=false
```

Create the database and apply migrations:

```bash
createdb doculens
psql -d doculens -c 'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
psql -d doculens -c 'CREATE EXTENSION IF NOT EXISTS vector;'
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
NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-audience
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
