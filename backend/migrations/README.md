# Database Migrations

This directory contains SQL migration scripts for the DocuLens database.

## Files

- **001_initial_schema.sql**: Creates users, courses, and documents tables with all indexes and constraints
- **001_initial_schema_rollback.sql**: Drops all tables (use for rollback)
- **002_add_vector_embeddings.sql**: Adds pgvector extension and embedding column for RAG functionality
- **002_add_vector_embeddings_rollback.sql**: Removes embedding column and index
- **run_migration.py**: Python script to run migrations

## Running Migrations

### Method 1: Using psql (Recommended)

```bash
# Make sure your .env file has the correct DATABASE_URL

# Connect to database
psql $DATABASE_URL

# Or if using default credentials:
psql -U doculens -d doculens

# Run the migration
\i migrations/001_initial_schema.sql

# Verify tables were created
\dt

# Exit
\q
```

### Method 2: Using the Python script

```bash
cd backend
source venv/bin/activate

# Run migration
python run_migration.py migrations/001_initial_schema.sql

# The script will:
# - Connect to your DATABASE_URL
# - Execute the SQL file
# - Show success/error messages
# - List all tables in the database
```

### Method 3: Direct psql command

```bash
# Run migration directly from command line
psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

## Rollback

To undo the migration and drop all tables:

```bash
# WARNING: This will delete all data!
psql $DATABASE_URL -f migrations/001_initial_schema_rollback.sql
```

## Database Schema

After running the migration, you will have:

### Tables
1. **users** - User accounts synced from Auth0
2. **courses** - Course organization for grouping documents
3. **documents** - Processed note documents

### Relationships
- Users (1:N) → Courses
- Courses (1:N) → Documents
- Users (1:N) → Documents

### Features
- UUID primary keys
- Soft deletes (status field: 'active' or 'trash')
- Automatic timestamp updates (created_at, updated_at)
- Foreign key constraints with CASCADE delete
- Optimized indexes for queries
- JSONB metadata field in documents
- Full audit trail with deleted_at timestamps

## Verifying Migration

After running the migration, verify with:

```sql
-- List all tables
\dt

-- Check users table
\d users

-- Check courses table
\d courses

-- Check documents table
\d documents

-- List all indexes
\di

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

## Using Alembic (Alternative)

If you prefer to use Alembic for migrations:

```bash
cd backend
source venv/bin/activate

# Generate migration from models
alembic revision --autogenerate -m "Create initial tables"

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

Note: You'll need to fix PostgreSQL permissions first for Alembic to work (see main README).
