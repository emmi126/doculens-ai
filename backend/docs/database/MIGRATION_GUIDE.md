# Database Migration Guide - Quick Start

This guide will help you run the database migration for DocuLens.

## Step-by-Step Instructions

### Step 1: Set Up PostgreSQL Database

Choose one of the following methods:

#### Option A: Automated Setup (Easiest)
```bash
cd backend
./setup_database.sh
```

#### Option B: Manual SQL Script
```bash
cd backend
sudo -u postgres psql -f setup_database_manual.sql
```

#### Option C: Manual Commands
See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed manual setup instructions.

---

### Step 2: Verify Database Connection

Test that the database is accessible:

```bash
# Test connection
psql -h localhost -U doculens -d doculens

# You should see:
# doculens=>

# Type \q to exit
```

---

### Step 3: Update Environment Variables

Make sure your `.env` file has the correct DATABASE_URL:

```bash
# backend/.env
DATABASE_URL=postgresql://doculens:password@localhost:5432/doculens
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_AUDIENCE=your-api-audience
GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json
ANTHROPIC_API_KEY=sk-ant-...
```

---

### Step 4: Run the Migration

Choose one method:

#### Method 1: Python Script (Recommended)
```bash
cd backend
source venv/bin/activate
python run_migration.py migrations/001_initial_schema.sql
```

This will:
- ✓ Create users table
- ✓ Create courses table
- ✓ Create documents table
- ✓ Create all indexes
- ✓ Set up triggers for auto-updating timestamps
- ✓ Show you all tables created

#### Method 2: Direct psql
```bash
psql -U doculens -d doculens -f migrations/001_initial_schema.sql
```

#### Method 3: Using DATABASE_URL
```bash
psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

---

### Step 5: Verify Migration Success

Check that tables were created:

```bash
psql -U doculens -d doculens -c "\dt"
```

Expected output:
```
             List of relations
 Schema |   Name    | Type  |  Owner
--------+-----------+-------+----------
 public | courses   | table | doculens
 public | documents | table | doculens
 public | users     | table | doculens
```

---

### Step 6: Start the Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting up application...
INFO:     Database ready
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 7: Test the API

1. **Open API Documentation:**
   - Navigate to http://localhost:8000/docs

2. **Test Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **View Available Endpoints:**
   - `/api/user/` - User profile (requires Auth0 token)
   - `/api/courses/` - Course management (requires Auth0 token)
   - `/api/documents/` - Document management (requires Auth0 token)
   - `/process-note` - Process images (requires Auth0 token)

---

## Troubleshooting

### Issue: Permission Denied

**Error:** `permission denied for schema public`

**Solution:**
```bash
sudo -u postgres psql -d doculens

# Inside psql:
ALTER SCHEMA public OWNER TO doculens;
GRANT ALL ON SCHEMA public TO doculens;
\q
```

Then run the migration again.

---

### Issue: Database Doesn't Exist

**Error:** `database "doculens" does not exist`

**Solution:**
```bash
sudo -u postgres psql

# Inside psql:
CREATE DATABASE doculens OWNER doculens;
\q
```

Then run the migration again.

---

### Issue: User Doesn't Exist

**Error:** `role "doculens" does not exist`

**Solution:**
```bash
sudo -u postgres psql

# Inside psql:
CREATE USER doculens WITH PASSWORD 'password';
CREATE DATABASE doculens OWNER doculens;
GRANT ALL PRIVILEGES ON DATABASE doculens TO doculens;
\q
```

Then run the migration again.

---

### Issue: Connection Refused

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # macOS

# Start PostgreSQL
sudo systemctl start postgresql   # Linux
brew services start postgresql    # macOS
```

---

## Rollback Migration

If you need to undo the migration:

```bash
# WARNING: This will delete all data!
python run_migration.py migrations/001_initial_schema_rollback.sql
```

---

## What the Migration Creates

### Tables

1. **users**
   - Stores user accounts synced from Auth0
   - Fields: id, auth0_user_id, email, name, avatar_url, email_verified, is_active, timestamps

2. **courses**
   - Organizes documents by course
   - Fields: id, user_id, name, description, color, icon, status, timestamps
   - Soft deletes with status field

3. **documents**
   - Stores processed note documents
   - Fields: id, course_id, user_id, title, original_text, formatted_note, excerpt, image_path, status, processing_time, metadata (JSONB), timestamps
   - Soft deletes with status field

### Relationships

```
users (1) ─────→ (N) courses
  │
  └──────────────→ (N) documents
                      ↑
courses (1) ──────────┘ (N)
```

### Indexes

- Primary keys on all tables (UUIDs)
- Foreign key indexes for fast joins
- Composite indexes for common queries
- JSONB index on documents.metadata
- Optional full-text search indexes (commented out)

### Features

- ✓ UUID primary keys
- ✓ Foreign key constraints with CASCADE delete
- ✓ Automatic timestamp updates (updated_at)
- ✓ Soft deletes (status field: active/trash)
- ✓ JSONB metadata for flexible data storage
- ✓ Optimized indexes for queries
- ✓ CHECK constraints for data integrity

---

## Next Steps

1. **Set up Auth0** for authentication
2. **Test API endpoints** with authentication
3. **Set up frontend** to connect to the backend
4. **Configure production database** for deployment

---

## Using Alembic (Alternative)

If you fix the PostgreSQL permissions, you can use Alembic instead:

```bash
cd backend
source venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Create initial tables"

# Apply migration
alembic upgrade head

# Check current version
alembic current
```

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for details.

---

## Support

For more detailed information:
- **Full setup guide:** [DATABASE_SETUP.md](DATABASE_SETUP.md)
- **Migration files:** [migrations/README.md](migrations/README.md)
- **Design document:** [docs/DESIGN_DOC_DATA_PERSISTENCE.md](docs/DESIGN_DOC_DATA_PERSISTENCE.md)

If you continue to have issues, check the PostgreSQL logs:
```bash
# Linux
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# macOS
tail -f /usr/local/var/log/postgres.log
```
