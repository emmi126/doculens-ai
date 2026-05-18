"""
Vector store service for RAG (Retrieval-Augmented Generation) operations.
Handles semantic search using pgvector and course-level context retrieval.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
import logging
from uuid import UUID

from models.document import Document
from models.course import Course

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for vector-based document retrieval and similarity search"""

    def __init__(self):
        """Initialize the vector store service"""
        logger.info("Vector store service initialized")

    def find_similar_documents(
        self,
        db: Session,
        query_embedding: List[float],
        course_id: UUID,
        top_k: int = 3,
        exclude_document_id: Optional[UUID] = None,
        similarity_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Find documents similar to the query embedding within the same course.

        Args:
            db: Database session
            query_embedding: Query vector (384 dimensions)
            course_id: Course ID to filter by (ensures course-level isolation)
            top_k: Number of similar documents to return
            exclude_document_id: Optional document ID to exclude (e.g., the query document itself)
            similarity_threshold: Minimum cosine similarity score (0-1)

        Returns:
            List of (Document, similarity_score) tuples, ordered by similarity (highest first)
        """
        try:
            # Build query with vector similarity search
            query = db.query(
                Document,
                (1 - Document.embedding.cosine_distance(query_embedding)).label('similarity')
            ).filter(
                Document.course_id == course_id,
                Document.status == 'active',
                Document.embedding.isnot(None)  # Only documents with embeddings
            )

            # Exclude specific document if needed
            if exclude_document_id:
                query = query.filter(Document.id != exclude_document_id)

            # Order by similarity and limit results
            results = query.order_by(
                Document.embedding.cosine_distance(query_embedding)
            ).limit(top_k).all()

            # Filter by similarity threshold and convert to list of tuples
            similar_docs = [
                (doc, similarity) for doc, similarity in results
                if similarity >= similarity_threshold
            ]

            logger.info(
                f"Found {len(similar_docs)} similar documents for course {course_id} "
                f"(threshold={similarity_threshold}, top_k={top_k})"
            )

            return similar_docs

        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            return []

    def find_related_notes(
        self,
        db: Session,
        document_id: UUID,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find notes related to a specific document.

        Args:
            db: Database session
            document_id: Source document ID
            top_k: Number of related notes to return

        Returns:
            List of related note information (id, title, excerpt, similarity)
        """
        try:
            # Get the source document
            source_doc = db.query(Document).filter(
                Document.id == document_id,
                Document.status == 'active'
            ).first()

            if not source_doc:
                logger.warning(f"Document {document_id} not found")
                return []

            if source_doc.embedding is None or len(source_doc.embedding) == 0:
                logger.warning(f"Document {document_id} has no embedding")
                return []

            # Find similar documents in the same course
            similar_docs = self.find_similar_documents(
                db=db,
                query_embedding=source_doc.embedding,
                course_id=source_doc.course_id,
                top_k=top_k,
                exclude_document_id=document_id,
                similarity_threshold=0.3  # Only show reasonably similar notes
            )

            # Format results for frontend
            related_notes = []
            for doc, similarity in similar_docs:
                related_notes.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'excerpt': doc.excerpt or doc.formatted_note[:200],
                    'similarity': round(similarity, 3),
                    'created_at': doc.created_at.isoformat() if doc.created_at else None
                })

            return related_notes

        except Exception as e:
            logger.error(f"Error finding related notes: {e}")
            return []

    def get_context_for_new_note(
        self,
        db: Session,
        new_note_text: str,
        new_note_embedding: List[float],
        course_id: UUID,
        top_k: int = 3
    ) -> List[Dict[str, str]]:
        """
        Retrieve historical context for a new note being processed.
        This is used by the LLM to generate integrated notes.

        Args:
            db: Database session
            new_note_text: OCR text of the new note
            new_note_embedding: Embedding of the new note
            course_id: Course ID
            top_k: Number of historical notes to retrieve

        Returns:
            List of context dictionaries with 'title', 'content', 'created_at'
        """
        try:
            # Find similar historical notes
            similar_docs = self.find_similar_documents(
                db=db,
                query_embedding=new_note_embedding,
                course_id=course_id,
                top_k=top_k,
                similarity_threshold=0.4  # Higher threshold for context relevance
            )

            if not similar_docs:
                logger.info(f"No relevant historical context found for course {course_id}")
                return []

            # Format context for LLM prompt
            context = []
            for doc, similarity in similar_docs:
                context.append({
                    'title': doc.title,
                    'content': doc.formatted_note,
                    'created_at': doc.created_at.strftime('%Y-%m-%d') if doc.created_at else 'Unknown',
                    'similarity': round(similarity, 3)
                })

            logger.info(
                f"Retrieved {len(context)} historical notes as context "
                f"(similarities: {[c['similarity'] for c in context]})"
            )

            return context

        except Exception as e:
            logger.error(f"Error getting context for new note: {e}")
            return []

    def update_document_embedding(
        self,
        db: Session,
        document_id: UUID,
        embedding: List[float]
    ) -> bool:
        """
        Update the embedding vector for an existing document.

        Args:
            db: Database session
            document_id: Document ID
            embedding: New embedding vector

        Returns:
            True if successful, False otherwise
        """
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()

            if not doc:
                logger.warning(f"Document {document_id} not found")
                return False

            doc.embedding = embedding
            db.commit()

            logger.info(f"Updated embedding for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating document embedding: {e}")
            db.rollback()
            return False

    def get_documents_without_embeddings(
        self,
        db: Session,
        limit: int = 100
    ) -> List[Document]:
        """
        Get documents that don't have embeddings yet (for batch indexing).

        Args:
            db: Database session
            limit: Maximum number of documents to return

        Returns:
            List of documents without embeddings
        """
        try:
            docs = db.query(Document).filter(
                Document.status == 'active',
                Document.embedding.is_(None)
            ).limit(limit).all()

            logger.info(f"Found {len(docs)} documents without embeddings")
            return docs

        except Exception as e:
            logger.error(f"Error getting documents without embeddings: {e}")
            return []

    def get_course_document_count(
        self,
        db: Session,
        course_id: UUID
    ) -> Dict[str, int]:
        """
        Get statistics about documents in a course.

        Args:
            db: Database session
            course_id: Course ID

        Returns:
            Dictionary with 'total', 'with_embeddings', 'without_embeddings'
        """
        try:
            total = db.query(Document).filter(
                Document.course_id == course_id,
                Document.status == 'active'
            ).count()

            with_embeddings = db.query(Document).filter(
                Document.course_id == course_id,
                Document.status == 'active',
                Document.embedding.isnot(None)
            ).count()

            return {
                'total': total,
                'with_embeddings': with_embeddings,
                'without_embeddings': total - with_embeddings
            }

        except Exception as e:
            logger.error(f"Error getting course document count: {e}")
            return {'total': 0, 'with_embeddings': 0, 'without_embeddings': 0}


# Singleton instance
_vector_store_service = None

def get_vector_store() -> VectorStoreService:
    """Get or create the singleton vector store service instance"""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service
