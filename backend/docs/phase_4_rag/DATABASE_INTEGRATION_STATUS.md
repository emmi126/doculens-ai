# Database Integration Status

Phase 4 database integration is complete for local development.

## Verified Components

- PostgreSQL accepts connections on the configured database URL.
- The `users`, `courses`, and `documents` tables exist.
- The `pgcrypto` extension is installed.
- The `vector` extension is installed.
- The document embedding column uses 384 dimensions.
- The sentence-transformer embedding service produces 384-dimensional vectors.

## Required Runtime Configuration

Set `DATABASE_URL` in `backend/.env`, then apply both migrations before starting the API.

## Notes

This is an archival status document. Environment-specific passwords, machine paths, and obsolete installation troubleshooting have been removed. Consult the current README for setup instructions.
