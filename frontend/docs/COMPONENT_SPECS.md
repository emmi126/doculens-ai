# Component Specifications

## Technology Stack

### State Management: Zustand
All components use **Zustand** for global state management. Import from `@/lib/store`:

```typescript
import { useStore } from '@/lib/store';

// In a component
function MyComponent() {
  const courses = useStore((state) => state.courses);
  const addCourse = useStore((state) => state.addCourse);

  // ...
}
```

### Authentication: Auth0
All components use **Auth0** for authentication. Import from `@auth0/auth0-react`:

```typescript
import { useAuth0 } from '@auth0/auth0-react';

// In a component
function MyComponent() {
  const { user, isAuthenticated, loginWithRedirect, logout } = useAuth0();

  // ...
}
```

See `DESIGN_DOC_DASHBOARD.md` for complete Zustand store implementation and Auth0 configuration.

---

## Layout Components

### 1. DashboardLayout

**File**: `components/layout/DashboardLayout.tsx`

```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  // Implementation
}
```

**Structure**:
```tsx
<div className="h-screen flex flex-col">
  <Header />
  <div className="flex flex-1 overflow-hidden">
    <Sidebar />
    <main className="flex-1 overflow-auto">
      {children}
    </main>
  </div>
</div>
```

**Responsive Breakpoints**:
- Desktop: `min-width: 1024px` - Full layout
- Tablet: `768px - 1023px` - Collapsible sidebar
- Mobile: `max-width: 767px` - Overlay sidebar

---

### 2. Header

**File**: `components/layout/Header.tsx`

```typescript
interface HeaderProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
}

export default function Header({ user }: HeaderProps) {
  // Implementation
}
```

**HTML Structure**:
```html
<header className="h-16 bg-white border-b border-gray-200 px-6">
  <div className="flex items-center justify-between h-full">
    <!-- Left: Logo -->
    <div className="flex items-center space-x-3">
      <Camera className="w-6 h-6 text-blue-600" />
      <span className="text-xl font-bold text-gray-900">DocuLens</span>
    </div>

    <!-- Right: User Menu (Desktop) or Hamburger (Mobile) -->
    <div className="flex items-center space-x-4">
      <!-- User Dropdown Menu -->
    </div>
  </div>
</header>
```

**States**:
- Default
- User menu open
- Mobile menu open

---

### 3. Sidebar

**File**: `components/layout/Sidebar.tsx`

```typescript
interface SidebarProps {
  activeSection: 'docs' | 'trash';
  onSectionChange: (section: 'docs' | 'trash') => void;
  user: {
    name: string;
    email: string;
    avatar?: string;
  };
  isCollapsed?: boolean;
}
```

**HTML Structure**:
```html
<aside className="w-[280px] bg-gray-50 border-r border-gray-200 flex flex-col">
  <!-- Navigation (80%) -->
  <nav className="flex-[4] p-4 space-y-2">
    <!-- Docs Section -->
    <button className="nav-item active">
      <FileText className="w-5 h-5" />
      <span>Docs</span>
    </button>

    <!-- Trash Section -->
    <button className="nav-item">
      <Trash2 className="w-5 h-5" />
      <span>Trash</span>
    </button>
  </nav>

  <!-- Footer (20%) -->
  <div className="flex-1 border-t border-gray-200 p-4">
    <SidebarFooter user={user} />
  </div>
</aside>
```

**Navigation Item States**:
```css
/* Default */
.nav-item {
  @apply w-full flex items-center space-x-3 px-4 py-3 rounded-lg
         text-gray-700 hover:bg-gray-100 transition-colors;
}

/* Active */
.nav-item.active {
  @apply bg-blue-50 text-blue-600 font-medium;
}

/* Hover */
.nav-item:hover:not(.active) {
  @apply bg-gray-100;
}
```

**Collapsed State** (80px width):
```html
<aside className="w-20 bg-gray-50 border-r border-gray-200">
  <nav className="p-2">
    <button className="nav-item-collapsed">
      <FileText className="w-5 h-5" />
    </button>
  </nav>
</aside>
```

---

### 4. SidebarFooter

**File**: `components/layout/SidebarFooter.tsx`

```typescript
interface SidebarFooterProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
  };
}
```

**HTML Structure**:
```html
<div className="flex items-center space-x-3">
  <!-- Avatar -->
  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
    {user.avatar ? (
      <img src={user.avatar} alt={user.name} className="w-full h-full rounded-full" />
    ) : (
      <span className="text-white font-medium">
        {user.name.charAt(0)}
      </span>
    )}
  </div>

  <!-- User Info -->
  <div className="flex-1 min-w-0">
    <p className="text-sm font-medium text-gray-900 truncate">
      {user.name}
    </p>
    <p className="text-xs text-gray-500 truncate">
      {user.email}
    </p>
  </div>

  <!-- Settings Icon (Optional) -->
  <button className="p-1 hover:bg-gray-200 rounded">
    <Settings className="w-4 h-4 text-gray-500" />
  </button>
</div>
```

---

## Feature Components

### 5. DocumentList

**File**: `components/documents/DocumentList.tsx`

```typescript
interface DocumentListProps {
  documents: Document[];
  onDocumentClick: (id: string) => void;
  onDocumentDelete?: (id: string) => void;
  isLoading?: boolean;
  emptyMessage?: string;
}
```

**HTML Structure**:
```html
<div className="p-6 space-y-4">
  <!-- Header -->
  <div className="flex items-center justify-between mb-6">
    <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
    <div className="flex items-center space-x-3">
      <SearchBar />
      <NewDocButton />
    </div>
  </div>

  <!-- Document Cards -->
  <div className="space-y-3">
    {documents.map(doc => (
      <DocumentCard key={doc.id} document={doc} />
    ))}
  </div>
</div>
```

**Loading State**:
```html
<div className="space-y-3">
  {[1, 2, 3].map(i => (
    <div key={i} className="animate-pulse">
      <div className="h-24 bg-gray-200 rounded-lg"></div>
    </div>
  ))}
</div>
```

**Empty State**:
```html
<div className="flex flex-col items-center justify-center py-16">
  <FileText className="w-16 h-16 text-gray-300 mb-4" />
  <h3 className="text-lg font-medium text-gray-900 mb-2">
    No documents yet
  </h3>
  <p className="text-gray-500 mb-6">
    Click "New doc" to create your first note
  </p>
  <NewDocButton />
</div>
```

---

### 6. DocumentCard

**File**: `components/documents/DocumentCard.tsx`

```typescript
interface DocumentCardProps {
  document: Document;
  onClick: () => void;
  onDelete?: () => void;
  onRestore?: () => void;
}
```

**HTML Structure**:
```html
<div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
  <!-- Header Row -->
  <div className="flex items-start justify-between mb-2">
    <h3 className="text-lg font-semibold text-gray-900 flex-1">
      {document.title || 'Untitled Document'}
    </h3>
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-500">
        {formatDate(document.createdAt)}
      </span>
      <DropdownMenu>
        <MoreVertical className="w-4 h-4 text-gray-400" />
      </DropdownMenu>
    </div>
  </div>

  <!-- Excerpt -->
  <p className="text-sm text-gray-600 line-clamp-2 mb-3">
    {document.excerpt || document.formattedNote.slice(0, 150)}...
  </p>

  <!-- Metadata Row -->
  <div className="flex items-center space-x-4 text-xs text-gray-500">
    <span>
      {formatRelativeTime(document.createdAt)}
    </span>
    <span>•</span>
    <span>
      {countWords(document.formattedNote)} words
    </span>
    {document.metadata?.ocrConfidence && (
      <>
        <span>•</span>
        <span>
          {Math.round(document.metadata.ocrConfidence * 100)}% confidence
        </span>
      </>
    )}
  </div>
</div>
```

**Variants**:

**Trash Card** (with restore option):
```html
<div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
  <!-- ... same structure ... -->

  <!-- Footer with Restore/Delete -->
  <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-gray-200">
    <button className="text-sm text-blue-600 hover:text-blue-700">
      Restore
    </button>
    <button className="text-sm text-red-600 hover:text-red-700">
      Delete Permanently
    </button>
  </div>
</div>
```

---

### 7. SearchBar

**File**: `components/ui/SearchBar.tsx`

```typescript
interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onSearch?: (query: string) => void;
}
```

**HTML Structure**:
```html
<div className="relative w-full max-w-md">
  <!-- Search Icon -->
  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />

  <!-- Input -->
  <input
    type="text"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder || "Search documents..."}
    className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg
               focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  />

  <!-- Clear Button (if value exists) -->
  {value && (
    <button
      onClick={() => onChange('')}
      className="absolute right-3 top-1/2 -translate-y-1/2"
    >
      <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
    </button>
  )}
</div>
```

**States**:
- Empty
- With text
- Focused
- With results dropdown (future enhancement)

---

### 8. NewDocButton

**File**: `components/ui/NewDocButton.tsx` (or inline)

```typescript
interface NewDocButtonProps {
  onClick: () => void;
  disabled?: boolean;
}
```

**HTML Structure**:
```html
<button
  onClick={onClick}
  disabled={disabled}
  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white
             rounded-lg hover:bg-blue-700 transition-colors
             disabled:opacity-50 disabled:cursor-not-allowed"
>
  <Plus className="w-5 h-5" />
  <span>New doc</span>
</button>
```

**Variants**:
- Primary (default)
- Icon only (mobile)

---

## Page Components

### 9. Dashboard Page (`app/page.tsx`)

```typescript
'use client';

export default function DashboardPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Filter documents based on search
  const filteredDocuments = useMemo(() => {
    return documents.filter(doc =>
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.formattedNote.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [documents, searchQuery]);

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            My Documents
          </h1>
          <div className="flex items-center space-x-3">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
            />
            <NewDocButton onClick={() => router.push('/doc/new')} />
          </div>
        </div>

        {/* Document List */}
        <DocumentList
          documents={filteredDocuments}
          onDocumentClick={(id) => router.push(`/doc/${id}`)}
          isLoading={isLoading}
        />
      </div>
    </DashboardLayout>
  );
}
```

---

### 10. Trash Page (`app/trash/page.tsx`)

```typescript
'use client';

export default function TrashPage() {
  const [trashedDocs, setTrashedDocs] = useState<Document[]>([]);

  const handleRestore = (id: string) => {
    // API call to restore document
  };

  const handlePermanentDelete = (id: string) => {
    // API call to permanently delete
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Trash
        </h1>

        {trashedDocs.length === 0 ? (
          <EmptyState
            icon={Trash2}
            title="Trash is empty"
            description="Deleted documents will appear here"
          />
        ) : (
          <div className="space-y-3">
            {trashedDocs.map(doc => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onRestore={() => handleRestore(doc.id)}
                onDelete={() => handlePermanentDelete(doc.id)}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
```

---

## Utility Components

### 11. Avatar

**File**: `components/ui/Avatar.tsx`

```typescript
interface AvatarProps {
  src?: string;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  fallback?: string;
}

export default function Avatar({ src, alt, size = 'md', fallback }: AvatarProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
  };

  return (
    <div className={`rounded-full bg-blue-600 flex items-center justify-center ${sizeClasses[size]}`}>
      {src ? (
        <img src={src} alt={alt} className="w-full h-full rounded-full object-cover" />
      ) : (
        <span className="text-white font-medium">
          {fallback || alt.charAt(0).toUpperCase()}
        </span>
      )}
    </div>
  );
}
```

---

### 12. EmptyState

**File**: `components/documents/EmptyState.tsx`

```typescript
interface EmptyStateProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <Icon className="w-16 h-16 text-gray-300 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-gray-500 text-center mb-6 max-w-md">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
```

---

## Interaction Patterns

### Document Actions Dropdown

```typescript
const documentActions = [
  { label: 'Open', icon: ExternalLink, onClick: () => {} },
  { label: 'Rename', icon: Edit, onClick: () => {} },
  { label: 'Duplicate', icon: Copy, onClick: () => {} },
  { label: 'Move to Trash', icon: Trash2, onClick: () => {}, danger: true },
];
```

### Keyboard Shortcuts

```typescript
const shortcuts = {
  'cmd+k': 'Focus search',
  'cmd+n': 'New document',
  'esc': 'Close modal/clear search',
  '↑/↓': 'Navigate documents',
  'enter': 'Open selected document',
};
```

---

## Animation Guidelines

### Transitions
```css
/* Page transitions */
.page-enter {
  opacity: 0;
  transform: translateY(10px);
}

.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: all 200ms ease-out;
}

/* Card hover */
.card {
  transition: shadow 200ms ease-in-out;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Sidebar collapse */
.sidebar {
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Color Tokens

```typescript
export const colors = {
  // Brand
  brand: {
    primary: '#3b82f6',
    primaryHover: '#2563eb',
    primaryLight: '#eff6ff',
  },

  // Neutral
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  // Semantic
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
  info: '#3b82f6',
};
```

---

**Last Updated**: 2025-01-17
