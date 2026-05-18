# DocuLens Dashboard UI Design Document

## Overview

This document outlines the design and implementation plan for transforming DocuLens from a single-page note processing application into a full-featured dashboard with course-based document management capabilities.

## Goals

1. **Course Organization**: Allow users to organize documents by courses/subjects
2. **Document Management**: View, organize, and manage notes within each course
3. **Improved Navigation**: Clear navigation between courses, documents, and trash
4. **User Context**: Display user information and maintain user session
5. **Better UX**: Create a professional, application-like experience

## Current State vs. Proposed State

### Current State
- Single-page application
- Upload → Process → Display → Reset flow
- No document persistence
- No user management
- No organization structure

### Proposed State
- Multi-page dashboard application
- Course-based organization (Dashboard → Courses → Documents)
- Persistent storage with PostgreSQL
- User authentication and profiles
- Document organization by course with trash functionality
- Search and filter capabilities

## Information Architecture

```
Dashboard
├── Courses (Grid View)
│   ├── Course A
│   │   ├── Document 1
│   │   ├── Document 2
│   │   └── Document 3
│   ├── Course B
│   │   └── Document 4
│   └── Course C
│       └── Document 5
└── Trash
    ├── Deleted Courses
    └── Deleted Documents
```

## UI Structure

### Dashboard View (Course Grid)
```
┌─────────────────────────────────────────────────────────────┐
│  Header                                                      │
│  [Logo]                                              [User]  │
└─────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────────┐
│          │  Main Section Header                             │
│          │  [New Course]                [Search courses...] │
│          ├──────────────────────────────────────────────────┤
│ Sidebar  │                                                   │
│ (80%)    │  Course Grid                                      │
│          │  ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│ Courses  │  │ 📚 Math   │ │ 📚 CS     │ │ 📚 Physics│      │
│ Trash    │  │ 12 docs   │ │ 8 docs    │ │ 5 docs    │      │
│          │  │ Updated:  │ │ Updated:  │ │ Updated:  │      │
├──────────┤  │ 2 days ago│ │ 1 day ago │ │ 3 days ago│      │
│ Footer   │  └───────────┘ └───────────┘ └───────────┘      │
│ (20%)    │                                                   │
│          │  ┌───────────┐ ┌───────────┐                    │
│ [Avatar] │  │ 📚 Chem   │ │ + New     │                    │
│ Username │  │ 3 docs    │ │   Course  │                    │
└──────────┴──┴───────────┴─┴───────────┴────────────────────┘
```

### Course Detail View (Document List)
```
┌─────────────────────────────────────────────────────────────┐
│  Header                                                      │
│  [Logo]  /  Courses  /  Mathematics        [User]           │
└─────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────────┐
│          │  Course Header                                    │
│          │  📚 Mathematics             [New doc] [Search]    │
│          ├──────────────────────────────────────────────────┤
│ Sidebar  │                                                   │
│ (80%)    │  Document List                                    │
│          │  ┌─────────────────────────────────────────────┐ │
│ Courses  │  │ Chapter 1: Algebra              Oct 15      │ │
│ Trash    │  │ Linear equations and inequalities...        │ │
│          │  │ Created 2 days ago • 1,234 words       [⋮] │ │
│          │  └─────────────────────────────────────────────┘ │
├──────────┤  ┌─────────────────────────────────────────────┐ │
│ Footer   │  │ Chapter 2: Geometry                Oct 14   │ │
│ (20%)    │  │ Triangles, circles, and theorems...        │ │
│          │  │ Created 3 days ago • 856 words         [⋮] │ │
│ [Avatar] │  └─────────────────────────────────────────────┘ │
│ Username │                                                   │
└──────────┴──────────────────────────────────────────────────┘
```

## Data Models

### Course Model
```typescript
interface Course {
  id: string;
  name: string;
  description?: string;
  color?: string;              // For UI differentiation
  icon?: string;               // Emoji or icon identifier
  documentCount: number;       // Computed field
  status: 'active' | 'trash';
  createdAt: Date;
  updatedAt: Date;
  userId: string;              // Owner
}
```

### Document Model (Updated)
```typescript
interface Document {
  id: string;
  title: string;
  courseId: string;            // ← NEW: Belongs to a course
  originalText: string;        // OCR text
  formattedNote: string;       // Formatted markdown
  excerpt?: string;            // First 100 chars for preview
  imagePath?: string;          // Path to uploaded image
  status: 'active' | 'trash';
  createdAt: Date;
  updatedAt: Date;
  userId: string;              // Owner
  processingTime?: number;
  metadata?: {
    imageSize?: number;
    ocrConfidence?: number;
    context?: string;
  };
}
```

### User Model
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
}
```

## Component Breakdown

### 1. Layout Components

#### `DashboardLayout.tsx`
- **Purpose**: Main layout wrapper for the dashboard
- **Children**: Header, Sidebar, MainContent
- **Responsibilities**:
  - Overall page structure
  - Responsive breakpoints
  - Layout state management

#### `Header.tsx`
- **Purpose**: Top navigation bar with breadcrumbs
- **Elements**:
  - DocuLens logo (left)
  - Breadcrumbs (center) - "Courses / Mathematics"
  - User menu dropdown (right)
- **Props**:
  ```typescript
  interface HeaderProps {
    breadcrumbs?: Breadcrumb[];
    user?: {
      name: string;
      avatar?: string;
    };
  }
  ```

#### `Sidebar.tsx`
- **Purpose**: Left navigation panel
- **Sections**:
  - Navigation (80% height): Courses, Trash
  - User footer (20% height)
- **Props**:
  ```typescript
  interface SidebarProps {
    activeSection: 'courses' | 'trash';
    onSectionChange: (section: 'courses' | 'trash') => void;
    user: User;
  }
  ```

### 2. Course Components (NEW)

#### `CourseGrid.tsx`
- **Purpose**: Display courses in a grid layout
- **Features**:
  - Responsive grid (1-4 columns based on screen size)
  - Loading states
  - Empty state
  - Search/filter
- **Props**:
  ```typescript
  interface CourseGridProps {
    courses: Course[];
    onCourseClick: (id: string) => void;
    onCourseDelete?: (id: string) => void;
    isLoading?: boolean;
  }
  ```

#### `CourseCard.tsx`
- **Purpose**: Individual course card in the grid
- **Elements**:
  - Course icon/emoji
  - Course name
  - Document count
  - Last updated timestamp
  - Action menu (edit, delete)
- **Props**:
  ```typescript
  interface CourseCardProps {
    course: Course;
    onClick: () => void;
    onEdit?: () => void;
    onDelete?: () => void;
  }
  ```

#### `CreateCourseModal.tsx`
- **Purpose**: Modal for creating new courses
- **Fields**:
  - Course name (required)
  - Description (optional)
  - Icon/emoji picker
  - Color selector
- **Props**:
  ```typescript
  interface CreateCourseModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (course: Partial<Course>) => Promise<void>;
  }
  ```

### 3. Document Components

#### `DocumentList.tsx`
- **Purpose**: Display documents within a course
- **Features**:
  - List view (not grid)
  - Sort by date, title, etc.
  - Filter capabilities
  - Loading and empty states
- **Props**:
  ```typescript
  interface DocumentListProps {
    courseId: string;
    documents: Document[];
    onDocumentClick: (id: string) => void;
    onDocumentDelete?: (id: string) => void;
    isLoading?: boolean;
  }
  ```

#### `DocumentCard.tsx`
- **Purpose**: Individual document item in the list
- **Elements**:
  - Document title
  - Preview/excerpt
  - Metadata (created date, word count)
  - Action menu
- **Props**:
  ```typescript
  interface DocumentCardProps {
    document: Document;
    onClick: () => void;
    onDelete?: () => void;
  }
  ```

### 4. UI Components

#### `SearchBar.tsx`
- **Purpose**: Search courses or documents
- **Props**:
  ```typescript
  interface SearchBarProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    scope?: 'courses' | 'documents';
  }
  ```

#### `EmptyState.tsx`
- **Purpose**: Display when no content exists
- **Variants**: No courses, no documents, trash empty

## Page Routes

```typescript
// Updated route structure
/                          → Dashboard (course grid)
/courses                   → All courses (same as /)
/course/:id                → Course detail (document list)
/course/:courseId/doc/:id  → View/edit single document
/course/:id/new            → Create new document in course
/trash                     → Trashed courses and documents
/trash/courses             → Trashed courses only
/trash/documents           → Trashed documents only
/settings                  → User settings (future)
```

## State Management

### Technology: Zustand

We use **Zustand** for global state management due to its simplicity, TypeScript support, and minimal boilerplate.

**Installation:**
```bash
npm install zustand
```

### Global Store (lib/store.ts)

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AppState {
  // User state (managed by Auth0)
  user: User | null;
  setUser: (user: User | null) => void;

  // Course state
  courses: Course[];
  setCourses: (courses: Course[]) => void;
  addCourse: (course: Course) => void;
  updateCourse: (id: string, updates: Partial<Course>) => void;
  deleteCourse: (id: string) => void;
  restoreCourse: (id: string) => void;

  // Documents state
  documents: Record<string, Document[]>; // Keyed by courseId
  setDocuments: (courseId: string, documents: Document[]) => void;
  addDocument: (courseId: string, document: Document) => void;
  updateDocument: (id: string, updates: Partial<Document>) => void;
  deleteDocument: (id: string) => void;
  restoreDocument: (id: string) => void;

  // UI state
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  activeSection: 'courses' | 'trash';
  setActiveSection: (section: 'courses' | 'trash') => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

export const useStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // User
        user: null,
        setUser: (user) => set({ user }),

        // Courses
        courses: [],
        setCourses: (courses) => set({ courses }),
        addCourse: (course) => set((state) => ({
          courses: [...state.courses, course]
        })),
        updateCourse: (id, updates) => set((state) => ({
          courses: state.courses.map(c => c.id === id ? { ...c, ...updates } : c)
        })),
        deleteCourse: (id) => set((state) => ({
          courses: state.courses.filter(c => c.id !== id)
        })),
        restoreCourse: (id) => set((state) => ({
          courses: state.courses.map(c =>
            c.id === id ? { ...c, status: 'active' } : c
          )
        })),

        // Documents
        documents: {},
        setDocuments: (courseId, documents) => set((state) => ({
          documents: { ...state.documents, [courseId]: documents }
        })),
        addDocument: (courseId, document) => set((state) => ({
          documents: {
            ...state.documents,
            [courseId]: [...(state.documents[courseId] || []), document]
          }
        })),
        updateDocument: (id, updates) => set((state) => {
          const newDocuments = { ...state.documents };
          Object.keys(newDocuments).forEach(courseId => {
            newDocuments[courseId] = newDocuments[courseId].map(doc =>
              doc.id === id ? { ...doc, ...updates } : doc
            );
          });
          return { documents: newDocuments };
        }),
        deleteDocument: (id) => set((state) => {
          const newDocuments = { ...state.documents };
          Object.keys(newDocuments).forEach(courseId => {
            newDocuments[courseId] = newDocuments[courseId].filter(doc => doc.id !== id);
          });
          return { documents: newDocuments };
        }),
        restoreDocument: (id) => set((state) => {
          const newDocuments = { ...state.documents };
          Object.keys(newDocuments).forEach(courseId => {
            newDocuments[courseId] = newDocuments[courseId].map(doc =>
              doc.id === id ? { ...doc, status: 'active' } : doc
            );
          });
          return { documents: newDocuments };
        }),

        // UI State
        sidebarCollapsed: false,
        setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
        activeSection: 'courses',
        setActiveSection: (section) => set({ activeSection: section }),
        searchQuery: '',
        setSearchQuery: (query) => set({ searchQuery: query }),
      }),
      {
        name: 'doculens-storage',
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          // Don't persist user, courses, or documents (fetch from API)
        }),
      }
    )
  )
);
```

### Usage in Components

```typescript
// hooks/useCourses.ts
import { useStore } from '@/lib/store';

export function useCourses() {
  const courses = useStore((state) => state.courses);
  const addCourse = useStore((state) => state.addCourse);
  const updateCourse = useStore((state) => state.updateCourse);

  return { courses, addCourse, updateCourse };
}

// In a component
function CourseGrid() {
  const { courses, addCourse } = useCourses();

  // ...
}
```

## API Endpoints

### Course Endpoints (NEW)

```typescript
// Course management
GET    /api/courses                → List all courses for user
GET    /api/courses/:id            → Get single course
POST   /api/courses                → Create new course
PUT    /api/courses/:id            → Update course
DELETE /api/courses/:id            → Move to trash
POST   /api/courses/:id/restore    → Restore from trash
DELETE /api/courses/:id/permanent  → Permanently delete

// Course statistics
GET    /api/courses/:id/stats      → Get course stats (doc count, etc.)
```

### Document Endpoints (Updated)

```typescript
// Document management
GET    /api/courses/:courseId/documents     → List documents in course
GET    /api/documents/:id                   → Get single document
POST   /api/courses/:courseId/documents     → Create document in course
PUT    /api/documents/:id                   → Update document
DELETE /api/documents/:id                   → Move to trash
POST   /api/documents/:id/restore           → Restore from trash
DELETE /api/documents/:id/permanent         → Permanently delete
POST   /api/documents/:id/move              → Move to different course
```

### Search Endpoints

```typescript
GET    /api/search?q=&scope=courses         → Search courses
GET    /api/search?q=&scope=documents       → Search documents
GET    /api/search?q=                       → Search both
```

### Authentication

**Technology: Auth0**

We use **Auth0** for authentication to provide secure, scalable user management without building custom auth.

**Benefits:**
- Social login (Google, GitHub, etc.)
- Multi-factor authentication (MFA)
- Password security best practices
- Session management
- User management dashboard

**Setup:**
```bash
npm install @auth0/auth0-react
```

**Configuration (app/layout.tsx):**
```typescript
import { Auth0Provider } from '@auth0/auth0-react';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Auth0Provider
          domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN}
          clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID}
          authorizationParams={{
            redirect_uri: typeof window !== 'undefined' ? window.location.origin : '',
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          }}
        >
          {children}
        </Auth0Provider>
      </body>
    </html>
  );
}
```

**Usage in Components:**
```typescript
import { useAuth0 } from '@auth0/auth0-react';

function Header() {
  const { user, isAuthenticated, loginWithRedirect, logout } = useAuth0();

  if (!isAuthenticated) {
    return <button onClick={() => loginWithRedirect()}>Log In</button>;
  }

  return (
    <div>
      <span>{user.name}</span>
      <button onClick={() => logout()}>Log Out</button>
    </div>
  );
}
```

### User Endpoints

```typescript
GET    /api/user                   → Get current user profile (synced from Auth0)
PUT    /api/user                   → Update user profile
```

**Note:** Authentication is handled by Auth0. The backend validates Auth0 JWT tokens on each request.

## File Structure

```
frontend/
├── app/
│   ├── layout.tsx                      # Root layout
│   ├── page.tsx                        # Dashboard (course grid)
│   ├── courses/
│   │   └── page.tsx                    # Courses page (same as /)
│   ├── course/
│   │   ├── [id]/
│   │   │   ├── page.tsx                # Course detail (doc list)
│   │   │   ├── new/
│   │   │   │   └── page.tsx            # New document in course
│   │   │   └── doc/
│   │   │       └── [docId]/
│   │   │           └── page.tsx        # View/edit document
│   │   └── new/
│   │       └── page.tsx                # Create new course
│   ├── trash/
│   │   ├── page.tsx                    # All trash
│   │   ├── courses/
│   │   │   └── page.tsx                # Trashed courses
│   │   └── documents/
│   │       └── page.tsx                # Trashed documents
│   └── globals.css
├── components/
│   ├── layout/
│   │   ├── DashboardLayout.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── SidebarFooter.tsx
│   ├── courses/                        # NEW
│   │   ├── CourseGrid.tsx
│   │   ├── CourseCard.tsx
│   │   ├── CreateCourseModal.tsx
│   │   ├── EditCourseModal.tsx
│   │   └── CourseEmptyState.tsx
│   ├── documents/
│   │   ├── DocumentList.tsx
│   │   ├── DocumentCard.tsx
│   │   ├── DocumentView.tsx
│   │   └── EmptyState.tsx
│   ├── ui/
│   │   ├── SearchBar.tsx
│   │   ├── Button.tsx
│   │   ├── Modal.tsx                   # NEW
│   │   ├── IconPicker.tsx              # NEW
│   │   ├── ColorPicker.tsx             # NEW
│   │   └── Avatar.tsx
│   ├── ImageUploader.tsx
│   ├── LoadingSpinner.tsx
│   └── NoteDisplay.tsx
├── lib/
│   ├── api.ts                          # API client (extend)
│   ├── store.ts                        # State management
│   └── utils.ts                        # Helper functions
├── types/
│   ├── course.ts                       # NEW
│   ├── document.ts
│   └── user.ts
└── hooks/
    ├── useCourses.ts                   # NEW
    ├── useDocuments.ts
    ├── useUser.ts
    └── useSearch.ts
```

## UI/UX Specifications

### Design System

#### Colors
```typescript
const colors = {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    500: '#6b7280',
    700: '#374151',
    900: '#111827',
  },
  // Course card colors (8 options)
  courseColors: [
    '#ef4444', '#f59e0b', '#10b981', '#3b82f6',
    '#6366f1', '#8b5cf6', '#ec4899', '#14b8a6',
  ],
};
```

#### Spacing
- Course card size: `280px × 200px` (min)
- Course grid gap: `24px`
- Sidebar width: `280px` (expanded), `80px` (collapsed)
- Header height: `64px`

### Course Card Design

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

### Empty States

#### No Courses
```
┌─────────────────────────────────────┐
│            📚                       │
│      No courses yet                 │
│  Create your first course to        │
│    organize your notes              │
│                                     │
│      [+ Create Course]              │
└─────────────────────────────────────┘
```

#### No Documents in Course
```
┌─────────────────────────────────────┐
│            📄                       │
│    No documents in this course      │
│  Click "New doc" to add your        │
│       first note                    │
│                                     │
│        [+ New doc]                  │
└─────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Course Management (Week 1-2)
- [ ] Create Course data model and types
- [ ] Build `CourseGrid` and `CourseCard` components
- [ ] Implement `CreateCourseModal`
- [ ] Add course CRUD operations
- [ ] Create course detail page

### Phase 2: Document Integration (Week 2-3)
- [ ] Update Document model with `courseId`
- [ ] Modify `DocumentList` to work within courses
- [ ] Update create document flow to include course selection
- [ ] Add breadcrumbs navigation
- [ ] Implement document-to-course assignment

### Phase 3: Navigation & Layout (Week 3)
- [ ] Update `Sidebar` with Courses/Trash sections
- [ ] Implement routing structure
- [ ] Add breadcrumb navigation in header
- [ ] Create empty states for all views
- [ ] Responsive design for course grid

### Phase 4: Search & Filter (Week 4)
- [ ] Implement course search
- [ ] Add document search within course
- [ ] Global search across all courses
- [ ] Filter by course color/category
- [ ] Sort options

### Phase 5: Trash Management (Week 4-5)
- [ ] Course trash view
- [ ] Document trash view
- [ ] Restore functionality for both
- [ ] Permanent delete with confirmation
- [ ] Auto-delete after 30 days (backend)

### Phase 6: Backend Integration (Week 5-6)
- [ ] Set up PostgreSQL database
- [ ] Create course and document tables
- [ ] Implement all API endpoints
- [ ] Add authentication
- [ ] Connect frontend to real API
- [ ] Data migration tools

### Phase 7: Polish & Enhancement (Week 6-7)
- [ ] Icon/emoji picker for courses
- [ ] Color picker for course customization
- [ ] Drag-and-drop document organization
- [ ] Keyboard shortcuts
- [ ] Animations and transitions
- [ ] Performance optimization

## Database Schema (PostgreSQL)

See `backend/docs/DESIGN_DOC_DATA_PERSISTENCE.md` for detailed schema design.

### Key Tables
```sql
users
  - id (uuid, pk)
  - email (unique)
  - name
  - avatar_url
  - created_at
  - updated_at

courses
  - id (uuid, pk)
  - user_id (fk → users)
  - name
  - description
  - color
  - icon
  - status (active/trash)
  - created_at
  - updated_at
  - deleted_at

documents
  - id (uuid, pk)
  - course_id (fk → courses)
  - user_id (fk → users)
  - title
  - original_text
  - formatted_note
  - excerpt
  - image_path
  - status (active/trash)
  - processing_time
  - metadata (jsonb)
  - created_at
  - updated_at
  - deleted_at
```

## User Flows

### Create New Note Flow
1. User clicks "New doc" on course detail page
2. Redirected to `/course/:id/new`
3. Upload image (existing ImageUploader)
4. Add context (optional)
5. Click "Process"
6. OCR + LLM processing
7. Document saved to course
8. Redirect to document view or back to course

### Course Management Flow
1. User views course grid (dashboard)
2. Clicks "+ New Course"
3. Modal opens with form
4. Enter name, select icon, choose color
5. Submit → course created
6. Card appears in grid
7. Click card → view documents in course

## Testing Strategy

### Unit Tests
- Component rendering (courses and documents)
- State management logic
- API client functions
- Utility functions

### Integration Tests
- Course CRUD operations
- Document CRUD within courses
- Search functionality
- Trash/restore operations
- Cross-component navigation

### E2E Tests
- Complete user flows (create course → add document → view → delete)
- Search and filter across courses
- Mobile responsive behavior
- Course and document organization

## Accessibility Considerations

1. **Keyboard Navigation**
   - Tab through course cards and documents
   - Arrow keys for grid navigation
   - Enter/Space to activate

2. **Screen Readers**
   - Semantic HTML
   - ARIA labels for course cards
   - Announce course and document counts

3. **Visual**
   - Color contrast (WCAG AA)
   - Focus indicators on cards
   - Text resize support

## Performance Optimization

1. **Course Grid**: Lazy load course cards
2. **Document List**: Virtual scrolling for large lists
3. **Images**: Optimize and lazy load thumbnails
4. **Search**: Debounce input, cache results
5. **Route Prefetching**: Prefetch course data on hover

## Security Considerations

1. **Course Access**: Users can only access their own courses
2. **Document Isolation**: Documents only accessible within owned courses
3. **Input Validation**: Sanitize course names and descriptions
4. **Rate Limiting**: Prevent course/document spam creation

## Open Questions

1. **Course Sharing**: Allow sharing courses with other users?
2. **Course Templates**: Predefined course structures?
3. **Document Tags**: Additional organization within courses?
4. **Course Archive**: Separate archive section vs trash?
5. **Course Export**: Export entire course as ZIP?

## Success Metrics

1. **Organization**: Average courses per user
2. **Usage**: Documents per course
3. **Engagement**: Time spent in app, return rate
4. **Search**: Search queries per session
5. **Performance**: Course load time < 1s, document load < 2s

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand ✓
- **Authentication**: Auth0 ✓
- **Data Fetching**: React Query (recommended)
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: Auth0 JWT validation
- **OCR**: Google Cloud Vision
- **LLM**: Anthropic Claude

## References

- [Next.js App Router](https://nextjs.org/docs/app)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand State Management](https://github.com/pmndrs/zustand)
- [Auth0 React SDK](https://auth0.com/docs/quickstart/spa/react)
- [Auth0 Documentation](https://auth0.com/docs)
- [React Query](https://tanstack.com/query/latest)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Last Updated**: 2025-01-17
**Status**: Updated - Course-based Organization
**Owner**: Development Team
