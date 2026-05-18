# Database Setup Guide

This guide will help you set up PostgreSQL for DocuLens.

## Prerequisites

PostgreSQL must be installed on your system.

### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Check installation:**
```bash
psql --version
```

## Setup Options

You have three options to set up the database:

### Option 1: Automated Script (Recommended)

Run the provided setup script:

```bash
cd backend
./setup_database.sh
```

This will:
- Create the database `doculens`
- Create user `doculens` with password `password`
- Set up all necessary permissions
- Enable required PostgreSQL extensions

### Option 2: Manual SQL Script

If the automated script doesn't work, run the SQL script manually:

```bash
cd backend
sudo -u postgres psql -f setup_database_manual.sql
```

### Option 3: Step-by-Step Manual Setup

Run these commands in order:

1. **Access PostgreSQL as superuser:**
   ```bash
   sudo -u postgres psql
   ```

2. **Create user and database:**
   ```sql
   -- Create user
   CREATE USER doculens WITH PASSWORD 'password';

   -- Create database
   CREATE DATABASE doculens OWNER doculens;

   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE doculens TO doculens;
   ```

3. **Connect to the database:**
   ```sql
   \c doculens
   ```

4. **Set up schema permissions:**
   ```sql
   -- Grant schema permissions
   GRANT ALL ON SCHEMA public TO doculens;
   GRANT CREATE ON SCHEMA public TO doculens;
   ALTER SCHEMA public OWNER TO doculens;

   -- Grant default privileges
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO doculens;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO doculens;

   -- Enable UUID extension
   CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   ```

5. **Exit PostgreSQL:**
   ```sql
   \q
   ```

## Verify Database Access

Test that you can connect to the database:

```bash
# Try connecting
psql -h localhost -U doculens -d doculens

# If it works, you should see:
# psql (14.x)
# Type "help" for help.
# doculens=>

# Exit with:
\q
```

## Configure Environment

Update your `.env` file with the database connection string:

```bash
# In backend/.env
DATABASE_URL=postgresql://doculens:password@localhost:5432/doculens
```

## Run Migrations

Once the database is set up, run the initial migration:

### Method 1: Using Python script
```bash
cd backend
source venv/bin/activate
python run_migration.py migrations/001_initial_schema.sql
```

### Method 2: Using psql directly
```bash
psql -U doculens -d doculens -f migrations/001_initial_schema.sql
```

### Method 3: Using environment variable
```bash
psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

## Verify Migration

Check that tables were created:

```bash
psql -h localhost -U doculens -d doculens

# Inside psql:
\dt          -- List all tables (should show: users, courses, documents)
\d users     -- Show users table structure
\d courses   -- Show courses table structure
\d documents -- Show documents table structure
\di          -- List all indexes
\q           -- Exit
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

## Troubleshooting

### Permission Denied Errors

If you get "permission denied for schema public":

1. Make sure you ran the setup as postgres superuser
2. Verify schema ownership:
   ```sql
   SELECT nspname, nspowner::regrole
   FROM pg_namespace
   WHERE nspname = 'public';
   ```
   Should show `doculens` as owner.

3. Run this as postgres superuser:
   ```sql
   ALTER SCHEMA public OWNER TO doculens;
   ```

### Connection Refused

If you can't connect to PostgreSQL:

1. Check if PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list                # macOS
   ```

2. Start PostgreSQL if needed:
   ```bash
   sudo systemctl start postgresql   # Linux
   brew services start postgresql    # macOS
   ```

3. Check `pg_hba.conf` for connection settings:
   ```bash
   # Linux
   sudo nano /etc/postgresql/14/main/pg_hba.conf

   # macOS
   nano /usr/local/var/postgres/pg_hba.conf
   ```

   Make sure this line exists:
   ```
   local   all   all   md5
   ```

### Database Already Exists

If the database exists but has wrong permissions:

```bash
sudo -u postgres psql

# Inside psql:
DROP DATABASE IF EXISTS doculens;
DROP USER IF EXISTS doculens;

# Then run setup again
\q
```

## Next Steps

After successful migration:

1. **Start the backend server:**
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

2. **Test the API:**
   - Open http://localhost:8000/docs
   - You should see the FastAPI documentation

3. **Test database health:**
   ```bash
   curl http://localhost:8000/health
   ```

## Using Different Database Credentials

To use different credentials:

1. **Update setup script variables:**
   ```bash
   DB_NAME=mydb DB_USER=myuser DB_PASSWORD=mypass ./setup_database.sh
   ```

2. **Update .env file:**
   ```bash
   DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydb
   ```

3. **Run migrations with new credentials**

## Production Considerations

For production deployments:

1. **Use strong passwords** (not 'password')
2. **Enable SSL/TLS** connections
3. **Set up regular backups**
4. **Configure connection pooling** (already done in config.py)
5. **Use environment-specific .env files**
6. **Consider using managed database services** (AWS RDS, Google Cloud SQL, etc.)

## Support

If you encounter issues:

1. Check PostgreSQL logs:
   ```bash
   # Linux
   sudo tail -f /var/log/postgresql/postgresql-14-main.log

   # macOS
   tail -f /usr/local/var/log/postgres.log
   ```

2. Verify database URL is correct in `.env`

3. Check that all required packages are installed:
   ```bash
   pip install -r requirements.txt
   ```
