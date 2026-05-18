# Backend Data Persistence Design Document

## Overview

This document outlines the design and implementation plan for adding persistent data storage to DocuLens using PostgreSQL. The system will support user authentication, course organization, and document management with full CRUD operations.

## Goals

1. **Data Persistence**: Store users, courses, and documents permanently
2. **Relational Integrity**: Maintain relationships between users, courses, and documents
3. **Performance**: Optimize queries for fast retrieval and searching
4. **Scalability**: Design schema to handle growing data
5. **Security**: Implement proper authentication and authorization
6. **Backup & Recovery**: Ensure data safety and recoverability

## Current State vs. Proposed State

### Current State
- No persistent storage
- Temporary file uploads to local directory
- No user management
- No database
- Stateless API

### Proposed State
- PostgreSQL database
- User authentication with Auth0
- Course and document tables with relationships
- File storage (local or cloud)
- Database migrations and versioning
- Automated backups

## Technology Stack

### Database
- **PostgreSQL 14+**: Relational database with JSONB support
- **psycopg2**: PostgreSQL adapter for Python
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool

### Authentication
- **Auth0**: Managed authentication service
- **python-jose**: JWT validation (for Auth0 tokens)
- **authlib**: OAuth/OIDC client library

### File Storage
- **Local Storage**: Development (uploads/ directory)
- **AWS S3** or **Cloudinary**: Production (future)

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐
│   courses   │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐
│  documents  │
└─────────────┘
```

### Tables

#### users

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth0_user_id VARCHAR(255) UNIQUE NOT NULL,  -- Auth0 user ID (sub claim)
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(512),
  email_verified BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_auth0_user_id ON users(auth0_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Fields:**
- `id`: UUID primary key (internal)
- `auth0_user_id`: Auth0 user identifier (from JWT `sub` claim)
- `email`: User email (synced from Auth0)
- `name`: Display name (synced from Auth0)
- `avatar_url`: URL to avatar image (synced from Auth0)
- `email_verified`: Email verification status (synced from Auth0)
- `is_active`: Soft delete flag (for account deactivation)
- `created_at`: Account creation timestamp (first login)
- `updated_at`: Last update timestamp
- `last_login_at`: Last successful login

**Note:** User authentication is managed by Auth0. This table stores additional user data and provides a foreign key for courses/documents.

#### courses

```sql
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  color VARCHAR(7),  -- Hex color code (#RRGGBB)
  icon VARCHAR(50),  -- Emoji or icon identifier
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'trash')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_courses_user_id ON courses(user_id);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_courses_created_at ON courses(created_at DESC);
CREATE INDEX idx_courses_user_status ON courses(user_id, status);
```

**Fields:**
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `name`: Course name (e.g., "Mathematics", "Computer Science")
- `description`: Optional course description
- `color`: Hex color for UI customization
- `icon`: Emoji or icon identifier for visual distinction
- `status`: 'active' or 'trash'
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `deleted_at`: Soft delete timestamp (for trash functionality)

#### documents

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  original_text TEXT NOT NULL,
  formatted_note TEXT NOT NULL,
  excerpt VARCHAR(200),
  image_path VARCHAR(512),
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'trash')),
  processing_time REAL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_documents_course_id ON documents(course_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_course_status ON documents(course_id, status);
CREATE INDEX idx_documents_title_trgm ON documents USING gin (title gin_trgm_ops);
CREATE INDEX idx_documents_formatted_note_trgm ON documents USING gin (formatted_note gin_trgm_ops);
CREATE INDEX idx_documents_metadata ON documents USING gin (metadata);
```

**Fields:**
- `id`: UUID primary key
- `course_id`: Foreign key to courses table
- `user_id`: Foreign key to users table (for ownership)
- `title`: Document title
- `original_text`: Raw OCR text output
- `formatted_note`: LLM-formatted markdown content
- `excerpt`: First 150-200 characters for preview
- `image_path`: Path to uploaded image file
- `status`: 'active' or 'trash'
- `processing_time`: Time taken for OCR + LLM (seconds)
- `metadata`: JSONB field for flexible data storage
  ```json
  {
    "imageSize": 1024000,
    "ocrConfidence": 0.95,
    "context": "Machine learning lecture",
    "wordCount": 1234,
    "language": "en"
  }
  ```
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp
- `deleted_at`: Soft delete timestamp

### Additional Tables (Future)

#### sessions (NOT NEEDED - Auth0 handles sessions)

**Note:** Auth0 manages user sessions and refresh tokens. We don't need a sessions table.

#### audit_logs (for tracking changes)

```sql
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID,
  changes JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

## SQLAlchemy Models

### User Model

```python
from sqlalchemy import Column, String, Boolean, DateTime, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(512))
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def get_or_create_from_auth0(cls, db, auth0_user):
        """Get existing user or create new one from Auth0 user info"""
        user = db.query(cls).filter(cls.auth0_user_id == auth0_user['sub']).first()

        if not user:
            user = cls(
                auth0_user_id=auth0_user['sub'],
                email=auth0_user.get('email'),
                name=auth0_user.get('name') or auth0_user.get('email'),
                avatar_url=auth0_user.get('picture'),
                email_verified=auth0_user.get('email_verified', False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user
```

### Course Model

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UUID, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color
    icon = Column(String(50))
    status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('active', 'trash')", name='courses_status_check'),
    )

    # Relationships
    user = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")

    @property
    def document_count(self):
        """Computed property for document count"""
        return len([d for d in self.documents if d.status == 'active'])
```

### Document Model

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, UUID, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    original_text = Column(Text, nullable=False)
    formatted_note = Column(Text, nullable=False)
    excerpt = Column(String(200))
    image_path = Column(String(512))
    status = Column(String(20), default='active')
    processing_time = Column(Float)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('active', 'trash')", name='documents_status_check'),
    )

    # Relationships
    course = relationship("Course", back_populates="documents")
    user = relationship("User", back_populates="documents")
```

## Database Configuration

### Connection String

```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://doculens:password@localhost:5432/doculens"
    )

    # Connection pool settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Auth0
    auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
    auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
    auth0_algorithms: list = ["RS256"]  # Auth0 uses RS256

    class Config:
        env_file = ".env"

settings = Settings()
```

### Database Engine

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine with connection pool
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    echo=settings.debug  # SQL logging in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## API Endpoints Implementation

### Authentication with Auth0

**Installation:**
```bash
pip install python-jose[cryptography] requests
```

**Auth0 JWT Verification:**

```python
# services/auth_service.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import requests

from config import settings
from database import get_db
from models import User

security = HTTPBearer()

def get_jwks():
    """Fetch Auth0 public keys for JWT verification"""
    jwks_url = f'https://{settings.auth0_domain}/.well-known/jwks.json'
    response = requests.get(jwks_url)
    return response.json()

def verify_token(token: str) -> dict:
    """Verify Auth0 JWT token"""
    try:
        # Get public key from Auth0
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)

        # Find the right key
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")

        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=settings.auth0_algorithms,
            audience=settings.auth0_audience,
            issuer=f'https://{settings.auth0_domain}/'
        )

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from Auth0 token"""
    token = credentials.credentials

    # Verify Auth0 token
    auth0_user = verify_token(token)

    # Get or create user in our database
    user = User.get_or_create_from_auth0(db, auth0_user)

    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()

    return user
```

**Usage in Routes:**

```python
# routes/courses.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Course
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("/")
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all courses for authenticated user"""
    courses = db.query(Course).filter(
        Course.user_id == current_user.id,
        Course.status == 'active'
    ).all()

    return courses
```

**User Endpoints:**

```python
# routes/user.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "avatar": current_user.avatar_url,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at
    }

@router.put("/")
async def update_user_profile(
    name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if name:
        current_user.name = name

    db.commit()

    return {"message": "Profile updated"}
```

**Note:** User registration and login are handled by Auth0. The frontend redirects to Auth0's Universal Login page.

### Course Endpoints

```python
# routes/courses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Course, User
from routes.auth import get_current_user

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("/")
async def list_courses(
    status: str = 'active',
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    courses = db.query(Course).filter(
        Course.user_id == current_user.id,
        Course.status == status
    ).order_by(Course.updated_at.desc()).all()

    return [
        {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "color": course.color,
            "icon": course.icon,
            "documentCount": course.document_count,
            "status": course.status,
            "createdAt": course.created_at,
            "updatedAt": course.updated_at
        }
        for course in courses
    ]

@router.post("/")
async def create_course(
    name: str,
    description: str = None,
    color: str = None,
    icon: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = Course(
        user_id=current_user.id,
        name=name,
        description=description,
        color=color,
        icon=icon
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return {"id": course.id, "name": course.name}

@router.get("/{course_id}")
async def get_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "color": course.color,
        "icon": course.icon,
        "documentCount": course.document_count,
        "status": course.status,
        "createdAt": course.created_at,
        "updatedAt": course.updated_at
    }

@router.put("/{course_id}")
async def update_course(
    course_id: str,
    name: str = None,
    description: str = None,
    color: str = None,
    icon: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if name: course.name = name
    if description is not None: course.description = description
    if color: course.color = color
    if icon: course.icon = icon

    course.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Course updated"}

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Soft delete
    course.status = 'trash'
    course.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Course moved to trash"}
```

## Database Migrations

### Using Alembic

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Configure alembic.ini
sqlalchemy.url = postgresql://doculens:password@localhost:5432/doculens

# Generate migration
alembic revision --autogenerate -m "create initial tables"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Initial Migration

```python
# alembic/versions/001_create_initial_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('avatar_url', sa.String(512)),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime(timezone=True))
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create courses table
    # ... similar pattern for courses and documents

def downgrade():
    op.drop_table('documents')
    op.drop_table('courses')
    op.drop_table('users')
```

## File Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   ├── 001_create_initial_tables.py
│   │   ├── 002_add_sessions_table.py
│   │   └── 003_add_audit_logs.py
│   ├── env.py
│   └── script.py.mako
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── course.py
│   └── document.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── courses.py
│   ├── documents.py
│   └── search.py
├── services/
│   ├── __init__.py
│   ├── ocr_service.py          # Existing
│   ├── llm_service.py          # Existing
│   ├── auth_service.py         # NEW
│   └── storage_service.py      # NEW
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── course.py
│   └── document.py
├── database.py                  # NEW
├── config.py                    # Update
├── main.py                      # Update
└── requirements.txt             # Update
```

## Performance Optimization

### Indexing Strategy

1. **Primary Indexes**: All foreign keys
2. **Composite Indexes**: `(user_id, status)` for fast filtering
3. **Full-Text Search**: GIN indexes on text fields
4. **Time-based**: Indexes on `created_at DESC` for sorting

### Query Optimization

```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import joinedload

courses = db.query(Course).options(
    joinedload(Course.documents)
).filter(Course.user_id == user_id).all()

# Use select_related for count queries
from sqlalchemy import func

course_stats = db.query(
    Course.id,
    Course.name,
    func.count(Document.id).label('doc_count')
).join(Document).group_by(Course.id).all()
```

### Connection Pooling

```python
# Configure connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Maintain 10 connections
    max_overflow=20,     # Allow 20 additional connections
    pool_timeout=30,     # Wait 30s for connection
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="doculens"

# Create backup
pg_dump -U doculens $DB_NAME > "$BACKUP_DIR/doculens_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/doculens_$TIMESTAMP.sql"

# Delete backups older than 30 days
find $BACKUP_DIR -name "doculens_*.sql.gz" -mtime +30 -delete
```

### Restore from Backup

```bash
# Restore database
gunzip -c /backups/postgres/doculens_20250117.sql.gz | psql -U doculens doculens
```

## Security Best Practices

1. **Authentication**: Auth0 manages passwords, MFA, and login security
2. **JWT Validation**: Verify Auth0 JWT signatures using JWKS (public keys)
3. **Token Verification**: Validate audience, issuer, and expiration on every request
4. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
5. **Authorization**: Check user ownership on every query
6. **Environment Variables**: Never commit secrets (Auth0 domain, audience)
7. **Database Access**: Restrict to application user only
8. **Connection Security**: Use SSL/TLS for database connections in production
9. **CORS**: Restrict allowed origins to frontend domains only
10. **Rate Limiting**: Implement rate limiting on API endpoints

## Testing Strategy

### Unit Tests

```python
# tests/test_models.py
def test_create_user(db_session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"

def test_cascade_delete(db_session):
    user = User(email="test@example.com")
    course = Course(user=user, name="Math")
    doc = Document(course=course, user=user, title="Chapter 1")

    db_session.add_all([user, course, doc])
    db_session.commit()

    # Delete course should cascade to documents
    db_session.delete(course)
    db_session.commit()

    assert db_session.query(Document).filter(Document.id == doc.id).first() is None
```

### Integration Tests

```python
# tests/test_api.py
def test_create_course_authenticated(client, auth_token):
    response = client.post(
        "/api/courses",
        json={"name": "Mathematics"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Mathematics"

def test_list_user_courses_only(client, user1_token, user2_token):
    # Create course as user1
    client.post("/api/courses", json={"name": "Math"}, headers={"Authorization": f"Bearer {user1_token}"})

    # List courses as user2
    response = client.get("/api/courses", headers={"Authorization": f"Bearer {user2_token}"})

    # User2 should not see user1's courses
    assert len(response.json()) == 0
```

## Deployment Checklist

- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Set up automated backups
- [ ] Configure SSL certificates
- [ ] Set up monitoring (query performance, errors)
- [ ] Configure connection pooling
- [ ] Test backup restoration
- [ ] Set up replication (optional)
- [ ] Configure rate limiting
- [ ] Enable query logging for slow queries

## Monitoring & Maintenance

### Health Checks

```python
@app.get("/api/health/db")
async def database_health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Query Performance Monitoring

```python
# Add query timing middleware
import time
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 1.0:  # Log slow queries (> 1 second)
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
```

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [FastAPI Database](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Last Updated**: 2025-01-17
**Status**: Design Complete
**Owner**: Backend Team
