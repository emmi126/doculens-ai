# DocuLens Design Update Summary

## Overview

This document summarizes the updated design for DocuLens, incorporating a **course-based organization system** and **PostgreSQL data persistence**.

## Key Changes

### 1. Information Architecture Update

**Previous Design:**
```
Dashboard → Documents (flat list)
```

**New Design:**
```
Dashboard → Courses (grid view) → Documents (list view per course)
```

Users now organize their notes by courses/subjects, providing better organization and context.

## Documentation Delivered

### Frontend Documentation (in `frontend/docs/`)

#### 1. DESIGN_DOC_DASHBOARD.md
**Comprehensive UI/UX design specification**

Key Sections:
- **Information Architecture**: Course → Document hierarchy
- **Data Models**:
  - `Course` model with color, icon, description
  - `Document` model with `courseId` foreign key
  - `User` model for authentication
- **Components**:
  - Course components: `CourseGrid`, `CourseCard`, `CreateCourseModal`
  - Document components: Updated to work within courses
  - Layout components: `DashboardLayout`, `Header`, `Sidebar`
- **Routes**:
  - `/` - Course grid
  - `/course/:id` - Document list for course
  - `/course/:courseId/doc/:id` - View/edit document
  - `/trash` - Trashed courses and documents
- **Implementation Phases**: 7-week roadmap
  - Phase 1: Course Management
  - Phase 2: Document Integration
  - Phase 3: Navigation & Layout
  - Phase 4: Search & Filter
  - Phase 5: Trash Management
  - Phase 6: Backend Integration
  - Phase 7: Polish & Enhancement

#### 2. COMPONENT_SPECS.md
**Detailed component specifications**

Includes:
- Complete TypeScript interfaces for all components
- HTML structure examples
- CSS classes and styling guidelines
- Component states (loading, empty, error)
- Animation guidelines
- Color tokens and design system

#### 3. MOCKUPS.md
**Visual wireframes (ASCII art)**

Includes:
- Desktop layout (1440px) with course grid
- Mobile layout (375px) with responsive design
- Course card designs
- Empty states (no courses, no documents)
- Loading states with shimmer animations
- Header and sidebar variations
- Color palette reference

### Backend Documentation (in `backend/docs/`)

#### 4. DESIGN_DOC_DATA_PERSISTENCE.md
**Complete PostgreSQL database design**

Key Sections:
- **Database Schema**:
  ```sql
  users
    ↓ (1:N)
  courses
    ↓ (1:N)
  documents
  ```

- **Tables**:
  - `users`: Authentication, profiles
  - `courses`: Course organization with color/icon customization
  - `documents`: Notes with OCR text and formatted content
  - `sessions`: Refresh tokens (future)
  - `audit_logs`: Change tracking (future)

- **SQLAlchemy Models**: Complete ORM models with relationships

- **API Implementation**:
  - Authentication endpoints (register, login, JWT)
  - Course CRUD endpoints
  - Document CRUD endpoints
  - Search endpoints

- **Database Migrations**: Alembic setup and migration examples

- **Performance**:
  - Indexing strategy
  - Connection pooling
  - Query optimization

- **Security**:
  - Password hashing with bcrypt
  - JWT authentication
  - Authorization checks
  - SQL injection prevention

- **Operations**:
  - Automated backup scripts
  - Health checks
  - Query performance monitoring
  - Testing strategies

## Key Features

### Course Organization

**Course Card Example:**
```
┌─────────────────────────────┐
│  📚                      [⋮] │
│                              │
│  Mathematics                 │
│                              │
│  12 documents                │
│  Updated 2 days ago          │
└─────────────────────────────┘
```

Features:
- Customizable icon/emoji
- Customizable color (8 preset colors)
- Document count display
- Last updated timestamp
- Action menu (edit, delete)

### Document Management

Documents now belong to courses:
- View all documents in a course
- Create new document within a course
- Move documents between courses
- Search documents within a course or globally

### Trash System

Hierarchical trash:
- Trashed courses (with all their documents)
- Trashed individual documents
- Restore functionality for both
- Permanent delete with confirmation
- Auto-delete after 30 days (backend)

## Database Schema Highlights

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url VARCHAR(512),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Courses Table
```sql
CREATE TABLE courses (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  color VARCHAR(7),     -- Hex color
  icon VARCHAR(50),     -- Emoji
  status VARCHAR(20),   -- 'active' or 'trash'
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  deleted_at TIMESTAMP
);
```

### Documents Table
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  user_id UUID REFERENCES users(id),
  title VARCHAR(500) NOT NULL,
  original_text TEXT NOT NULL,
  formatted_note TEXT NOT NULL,
  excerpt VARCHAR(200),
  image_path VARCHAR(512),
  status VARCHAR(20),
  processing_time REAL,
  metadata JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  deleted_at TIMESTAMP
);
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login (returns JWT)
- `GET /api/auth/user` - Get current user

### Courses
- `GET /api/courses` - List all courses
- `POST /api/courses` - Create course
- `GET /api/courses/:id` - Get course details
- `PUT /api/courses/:id` - Update course
- `DELETE /api/courses/:id` - Move to trash
- `POST /api/courses/:id/restore` - Restore from trash

### Documents
- `GET /api/courses/:courseId/documents` - List documents in course
- `POST /api/courses/:courseId/documents` - Create document
- `GET /api/documents/:id` - Get document
- `PUT /api/documents/:id` - Update document
- `DELETE /api/documents/:id` - Move to trash
- `POST /api/documents/:id/restore` - Restore from trash
- `POST /api/documents/:id/move` - Move to different course

### Search
- `GET /api/search?q=query&scope=courses` - Search courses
- `GET /api/search?q=query&scope=documents` - Search documents

## Technology Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand ✓ (Confirmed)
- **Authentication**: Auth0 ✓ (Confirmed)
- **Data Fetching**: React Query (recommended)
- **Icons**: Lucide React

**Key Libraries:**
```bash
npm install zustand @auth0/auth0-react @tanstack/react-query
```

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: Auth0 JWT Validation ✓ (Confirmed)
- **JWT Library**: python-jose[cryptography]

**Key Libraries:**
```bash
pip install fastapi sqlalchemy alembic psycopg2-binary python-jose[cryptography] requests
```

### Infrastructure
- **File Storage**: Local (dev), S3/Cloudinary (prod)
- **Backups**: Automated daily PostgreSQL dumps
- **Monitoring**: Query performance logging
- **Auth Provider**: Auth0

## Implementation Priority

### Phase 1: Foundation (Weeks 1-2)
1. Set up PostgreSQL database
2. Create SQLAlchemy models
3. Set up Auth0 account and configure application
4. Implement Auth0 JWT validation in backend
5. Configure Auth0Provider in frontend
6. Build course CRUD operations
7. Create frontend Course components

### Phase 2: Integration (Weeks 3-4)
1. Connect documents to courses
2. Update document creation flow
3. Implement search functionality
4. Add trash management

### Phase 3: Polish (Weeks 5-7)
1. Add icon/color pickers
2. Implement animations
3. Optimize performance
4. Add comprehensive testing
5. Deploy to production

## Next Steps

1. **Review all design documents** in `frontend/docs/` and `backend/docs/`

2. **Set up Auth0**:
   - Create Auth0 account at https://auth0.com
   - Create a new Application (Single Page Application)
   - Create an API in Auth0
   - Note down: Domain, Client ID, Audience
   - Configure allowed callback URLs, logout URLs, web origins

3. **Set up development environment**:
   - Install PostgreSQL
   - Create database and user
   - Configure environment variables:
     ```bash
     # Frontend (.env.local)
     NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
     NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
     NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-audience

     # Backend (.env)
     AUTH0_DOMAIN=your-domain.auth0.com
     AUTH0_AUDIENCE=your-api-audience
     DATABASE_URL=postgresql://user:password@localhost:5432/doculens
     ```

4. **Start with backend**:
   - Create database schema
   - Implement Auth0 JWT validation
   - Build course endpoints

5. **Then frontend**:
   - Configure Auth0Provider wrapper
   - Create layout components
   - Build course grid view
   - Implement course detail view

## Files Updated

- ✅ `CLAUDE.md` - Updated with references to all design docs
- ✅ `frontend/docs/DESIGN_DOC_DASHBOARD.md` - Complete rewrite with courses
- ✅ `frontend/docs/COMPONENT_SPECS.md` - Added course components
- ✅ `frontend/docs/MOCKUPS.md` - Added course view wireframes
- ✅ `backend/docs/DESIGN_DOC_DATA_PERSISTENCE.md` - NEW - PostgreSQL design

## Success Metrics

Track these KPIs after implementation:
- **Organization**: Average courses per user (target: 3-5)
- **Usage**: Average documents per course (target: 5-10)
- **Performance**: Course load time < 1s, document load < 2s
- **Engagement**: Return rate, session duration
- **Search**: Search usage and success rate

---

**Last Updated**: 2025-01-17
**Status**: Design Complete - Ready for Implementation
**Next**: Review design docs → Set up database → Begin Phase 1 implementation
