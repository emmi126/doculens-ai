# Related Notes Implementation

The related-notes interface displays documents selected by backend vector similarity.

## Data Flow

1. The document page supplies the current document ID and access token to `RelatedNotes`.
2. The component calls `GET /api/documents/{document_id}/related`.
3. The backend compares the current document embedding with active documents in the same course.
4. The frontend displays titles, excerpts, dates, and similarity percentages.

## Main Files

- `components/RelatedNotes.tsx`
- `lib/api.ts`
- `app/(authenticated)/document/[documentId]/page.tsx`

## Empty and Loading States

The component provides a loading indicator and an empty state when no sufficiently similar notes exist.

## Limitations

- Related-note cards do not currently navigate to their documents.
- API failures are treated as an empty result in the frontend client.
- Similarity explanations and user feedback are not implemented.

The UI is currently English and uses Canadian English date formatting.
