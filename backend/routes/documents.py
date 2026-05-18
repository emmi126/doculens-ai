"""Document routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from database import get_db
from models import Document, Course, User
from services.auth_service import get_current_user
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
from schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/courses/{course_id}/documents", response_model=List[DocumentResponse])
async def list_documents_in_course(
    course_id: str,
    status: str = 'active',
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents in a course"""
    # Verify course belongs to user
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    documents = db.query(Document).filter(
        Document.course_id == course_id,
        Document.status == status
    ).order_by(Document.created_at.desc()).all()

    return [
        DocumentResponse(
            id=str(doc.id),
            course_id=str(doc.course_id),
            title=doc.title,
            original_text=doc.original_text,
            formatted_note=doc.formatted_note,
            excerpt=doc.excerpt,
            image_path=doc.image_path,
            status=doc.status,
            processing_time=doc.processing_time,
            metadata=doc.doc_metadata,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
        for doc in documents
    ]


@router.post("/", response_model=dict)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document"""
    # Verify course belongs to user
    course = db.query(Course).filter(
        Course.id == document_data.course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Create excerpt from formatted note if not provided
    excerpt = document_data.excerpt
    if not excerpt and document_data.formatted_note:
        excerpt = document_data.formatted_note[:200]

    # Generate embedding for the formatted note
    embedding_service = get_embedding_service()
    try:
        # Use formatted note for embedding (it's cleaner than original OCR text)
        embedding = embedding_service.create_embedding(document_data.formatted_note)
        logger.info(f"Generated embedding for new document: {document_data.title}")
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        embedding = None

    document = Document(
        course_id=document_data.course_id,
        user_id=current_user.id,
        title=document_data.title,
        original_text=document_data.original_text,
        formatted_note=document_data.formatted_note,
        excerpt=excerpt,
        image_path=document_data.image_path,
        processing_time=document_data.processing_time,
        doc_metadata=document_data.metadata or {},
        embedding=embedding  # Store the embedding
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {"id": str(document.id), "title": document.title}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=str(document.id),
        course_id=str(document.course_id),
        title=document.title,
        original_text=document.original_text,
        formatted_note=document.formatted_note,
        excerpt=document.excerpt,
        image_path=document.image_path,
        status=document.status,
        processing_time=document.processing_time,
        metadata=document.doc_metadata,
        created_at=document.created_at,
        updated_at=document.updated_at
    )


@router.put("/{document_id}", response_model=dict)
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update fields if provided
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.formatted_note is not None:
        document.formatted_note = document_data.formatted_note

        # Regenerate embedding when formatted note is updated
        embedding_service = get_embedding_service()
        try:
            new_embedding = embedding_service.create_embedding(document_data.formatted_note)
            document.embedding = new_embedding
            logger.info(f"Regenerated embedding for updated document: {document_id}")
        except Exception as e:
            logger.error(f"Failed to regenerate embedding: {e}")

    if document_data.course_id is not None:
        # Verify new course belongs to user
        course = db.query(Course).filter(
            Course.id == document_data.course_id,
            Course.user_id == current_user.id
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Target course not found")
        document.course_id = document_data.course_id

    document.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Document updated"}


@router.delete("/{document_id}", response_model=dict)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move document to trash"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Soft delete
    document.status = 'trash'
    document.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Document moved to trash"}


@router.post("/{document_id}/restore", response_model=dict)
async def restore_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore document from trash"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.status == 'trash'
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found in trash")

    document.status = 'active'
    document.deleted_at = None
    db.commit()

    return {"message": "Document restored"}


@router.get("/{document_id}/related", response_model=List[dict])
async def get_related_notes(
    document_id: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notes related to a specific document using vector similarity.

    This endpoint uses RAG to find semantically similar notes within the same course.

    Args:
        document_id: Source document ID
        top_k: Number of related notes to return (default: 5)

    Returns:
        List of related notes with id, title, excerpt, similarity score, and created_at
    """
    # Verify document belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get related notes using vector store
    vector_store = get_vector_store()
    related_notes = vector_store.find_related_notes(
        db=db,
        document_id=document_id,
        top_k=top_k
    )

    return related_notes
