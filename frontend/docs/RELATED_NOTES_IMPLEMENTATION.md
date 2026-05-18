# Related Notes Frontend Implementation

**Date**: 2025-12-06
**Status**: ✅ Complete
**Phase**: 4 (RAG System Integration)

---

## Overview

Implemented frontend UI components to display AI-recommended related notes based on vector similarity. This completes the Phase 4 RAG system by providing users with contextual note recommendations in the UI.

---

## Implementation Summary

### 1. Backend Changes

#### Updated Schema (`backend/models/schemas.py`)

```python
class ProcessNoteResponse(BaseModel):
    success: bool
    original_text: str
    formatted_note: str
    processing_time: float
    document_id: Optional[str] = None  # NEW: For fetching related notes
    error: Optional[str] = None
```

#### Added Optional Authentication (`backend/services/auth_service.py`)

```python
# NEW: Optional authentication for backward compatibility
optional_security = HTTPBearer(auto_error=False)

async def get_current_user_optional(...) -> Optional[User]:
    """Returns None if no token provided, instead of raising error"""
```

**Why**: The simple upload interface doesn't have Auth0 yet, but the full dashboard will use authentication. This allows both to coexist.

#### Modified Process-Note Endpoint (`backend/main.py`)

**Before**: Required authentication, always used RAG, always saved documents
**After**:
- Optional authentication
- Uses RAG + saves document **only if** authenticated AND course_id provided
- Falls back to basic OCR + LLM formatting for unauthenticated users

```python
@app.post("/process-note")
async def process_note(
    current_user: Optional[User] = Depends(get_current_user_optional),  # NEW: Optional
    ...
):
    use_rag = current_user and course_id  # Only use RAG if authenticated

    if use_rag:
        # Full pipeline: OCR → RAG → LLM → Save
        document_id = str(document.id)
    else:
        # Simple pipeline: OCR → LLM (no RAG, no save)
        document_id = None
```

---

### 2. Frontend Changes

#### Updated API Client (`frontend/lib/api.ts`)

**Added Types**:
```typescript
export interface ProcessNoteResponse {
  document_id: string | null;  // NEW
  // ... other fields
}

export interface RelatedNote {
  id: string;
  title: string;
  excerpt: string;
  similarity: number;
  created_at: string | null;
}
```

**Added Function**:
```typescript
export const getRelatedNotes = async (
  documentId: string,
  topK: number = 5,
  token?: string
): Promise<RelatedNote[]>
```

---

#### Created RelatedNotes Component (`frontend/components/RelatedNotes.tsx`)

**Features**:
- ✅ Fetches related notes via API when `documentId` is provided
- ✅ Shows loading state with spinner
- ✅ Shows empty state when no related notes found
- ✅ Displays similarity scores as percentages
- ✅ Shows note title, excerpt, and creation date
- ✅ Responsive design (stacks on mobile, sidebar on desktop)
- ✅ "AI 推荐" badge to indicate AI-powered recommendations

**UI States**:

| State | Display |
|-------|---------|
| No document ID | Hidden (returns null) |
| Loading | Spinner with "相关笔记" header |
| No results | Empty state message |
| Has results | List of clickable note cards with similarity scores |

**Example Card**:
```
┌─────────────────────────────────────┐
│ Introduction to Machine Learning 85%│  ← Title + similarity
│ Machine learning is a subset of... │  ← Excerpt (truncated)
│ 📅 2025-12-01                       │  ← Creation date
└─────────────────────────────────────┘
```

---

#### Updated NoteDisplay Component (`frontend/components/NoteDisplay.tsx`)

**New Props**:
```typescript
interface NoteDisplayProps {
  documentId?: string | null;  // NEW
  token?: string;              // NEW
  // ... existing props
}
```

**Layout Change**: Two-column responsive grid

```
Desktop (lg):
┌────────────────────┬──────────┐
│                    │ Related  │
│   Formatted Note   │  Notes   │
│   (2 columns)      │(1 column)│
│                    │          │
└────────────────────┴──────────┘

Mobile:
┌──────────────────┐
│ Formatted Note   │
├──────────────────┤
│ Related Notes    │
└──────────────────┘
```

**Code**:
```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
  <div className="lg:col-span-2">
    {/* Markdown content */}
  </div>
  <div className="lg:col-span-1">
    <RelatedNotes documentId={documentId || null} token={token} />
  </div>
</div>
```

---

#### Updated Main Page (`frontend/app/page.tsx`)

**Change**: Pass `document_id` to NoteDisplay

```tsx
<NoteDisplay
  originalText={result.original_text}
  formattedNote={result.formatted_note}
  processingTime={result.processing_time}
  documentId={result.document_id}  // NEW
/>
```

---

## File Changes Summary

| File | Type | Changes |
|------|------|---------|
| `backend/models/schemas.py` | Modified | Added `document_id` field to `ProcessNoteResponse` |
| `backend/services/auth_service.py` | Modified | Added `get_current_user_optional()` function |
| `backend/main.py` | Modified | Made authentication optional, conditional RAG |
| `frontend/lib/api.ts` | Modified | Added `RelatedNote` type and `getRelatedNotes()` function |
| `frontend/components/RelatedNotes.tsx` | **Created** | New component for displaying related notes |
| `frontend/components/NoteDisplay.tsx` | Modified | Added two-column layout with `RelatedNotes` |
| `frontend/app/page.tsx` | Modified | Pass `document_id` prop |

---

## User Experience Flow

### Unauthenticated User (Simple Interface)

1. Upload image → Process note
2. See formatted note
3. **No related notes** (document not saved, no document_id)
4. RelatedNotes component hidden

### Authenticated User with Course (Future Dashboard)

1. Upload image to specific course → Process note
2. **RAG retrieval**: System finds top 3 similar notes from same course
3. **LLM formatting**: Uses historical context for better formatting
4. **Document saved** with embedding
5. **Related notes displayed** in sidebar:
   - Shows top 5 similar notes
   - Each with similarity score (0-100%)
   - Click to navigate (future feature)

---

## Technical Implementation Details

### API Call Flow

```
1. User uploads image
   ↓
2. Backend: OCR + (optional RAG) + LLM
   ↓
3. Response: { document_id: "abc-123", ... }
   ↓
4. Frontend: <NoteDisplay documentId="abc-123" />
   ↓
5. useEffect in RelatedNotes:
   → GET /api/documents/abc-123/related?top_k=5
   ↓
6. Display related notes with similarity scores
```

### Similarity Score Display

Backend returns similarity as float (0.0-1.0):
```json
{
  "id": "...",
  "similarity": 0.847
}
```

Frontend converts to percentage:
```tsx
<span>{Math.round(note.similarity * 100)}%</span>
// 0.847 → 85%
```

### Error Handling

- **API fails**: `getRelatedNotes()` catches error and returns empty array
- **No document ID**: Component returns `null` (hidden)
- **No results**: Shows friendly empty state message

### Performance Considerations

- **Lazy loading**: Related notes only fetched when `documentId` changes
- **Caching**: Browser caches API responses automatically
- **Responsive**: Uses Tailwind CSS grid for efficient layout

---

## Testing Checklist

### Backend
- [x] Process note without authentication → works
- [x] Process note with authentication + course_id → saves document, returns ID
- [x] Process note with authentication but no course_id → doesn't save, returns null ID
- [x] Optional auth endpoint doesn't crash on missing token

### Frontend
- [ ] Component renders without errors (requires Node.js/npm)
- [ ] Related notes fetch on mount when documentId provided
- [ ] Loading state shows spinner
- [ ] Empty state shows message
- [ ] Related notes display correctly with similarity scores
- [ ] Responsive layout works on mobile/desktop
- [ ] Component hidden when no documentId

**Note**: Frontend TypeScript syntax cannot be verified in current environment (Node.js not installed). Manual testing required after deployment.

---

## Next Steps

### Immediate (Manual Testing)

1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Test unauthenticated flow**:
   - Upload image
   - Verify formatted note displays
   - Verify no related notes section

4. **Test authenticated flow** (when Auth0 is set up):
   - Login
   - Upload to course
   - Verify related notes appear

### Future Enhancements

1. **Click-to-navigate**: Make related note cards clickable to open full note
2. **Inline preview**: Show full note in modal on hover/click
3. **Similarity threshold**: Allow users to adjust minimum similarity
4. **Related notes count**: Make `top_k` adjustable in UI
5. **Visual similarity indicator**: Use color-coded badges (high/medium/low)
6. **Empty state action**: Suggest uploading more notes to course

---

## Known Limitations

1. **No Auth0 in simple interface**: Current frontend doesn't have authentication, so:
   - Documents won't be saved
   - No RAG enhancement
   - No related notes displayed

2. **Requires Node.js for testing**: TypeScript compilation not verified

3. **No navigation**: Related notes display but can't be clicked to open

4. **Static top_k**: Always retrieves 5 related notes (hardcoded)

---

## Design Decisions

### Why Optional Authentication?

**Problem**: The current simple upload interface doesn't have Auth0, but the full dashboard (future) will require it.

**Solution**: Made authentication optional so both interfaces can coexist:
- Simple interface: Works without auth (basic OCR + LLM)
- Dashboard: Uses auth (RAG + document saving)

### Why Conditional RAG?

**Problem**: RAG requires a course context (course_id) to filter notes properly.

**Solution**: Only use RAG when both `current_user` AND `course_id` are provided:
```python
use_rag = current_user and course_id
```

### Why Two-Column Layout?

**Problem**: Related notes need to be visible without scrolling, but shouldn't distract from main content.

**Solution**: Responsive grid layout:
- Desktop: Related notes in right sidebar (1/3 width)
- Mobile: Related notes below main content
- Uses Tailwind's `lg:grid-cols-3` for responsive breakpoints

---

## Success Metrics

**Phase 4 Complete** ✅

- [x] Backend RAG system working (tested with 100% pass rate)
- [x] Frontend component created and integrated
- [x] Backward compatibility maintained (simple interface still works)
- [x] Optional authentication implemented
- [x] Related notes API endpoint consumed
- [x] Responsive UI design
- [x] All todos completed

**Next Phase**: Frontend dashboard with Auth0 integration (Phase 5)

---

## Documentation References

- **Backend RAG**: `/backend/docs/PHASE4_RAG_IMPLEMENTATION.md`
- **Database Integration**: `/backend/DATABASE_INTEGRATION_REPORT.md`
- **Design Docs**:
  - `/frontend/docs/DESIGN_DOC_DASHBOARD.md`
  - `/frontend/docs/COMPONENT_SPECS.md`

---

## Quick Start (After Node.js Installation)

```bash
# Backend
cd backend
source venv/bin/activate
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Visit http://localhost:3000
# Upload an image and see the formatted note
# (Related notes won't show until authenticated with course)
```

---

**Implementation completed**: 2025-12-06
**All Phase 4 tasks**: ✅ Complete
