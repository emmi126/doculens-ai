#!/usr/bin/env python3
"""
Script to generate embeddings for existing notes in the database.
Run this after enabling pgvector and adding the embedding column.

Usage:
    python scripts/index_existing_notes.py

This will:
1. Find all documents without embeddings
2. Generate embeddings using sentence-transformers
3. Update the database with the embeddings
"""

import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.document import Document
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def index_existing_notes(batch_size: int = 10, limit: int = None):
    """
    Generate embeddings for existing notes that don't have them yet.

    Args:
        batch_size: Number of documents to process in each batch
        limit: Maximum number of documents to process (None = process all)
    """
    logger.info("=" * 60)
    logger.info("Starting indexing of existing notes...")
    logger.info("=" * 60)

    # Initialize services
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()

    # Create database session
    db = SessionLocal()

    try:
        # Get documents without embeddings
        logger.info("Fetching documents without embeddings...")
        documents = vector_store.get_documents_without_embeddings(
            db=db,
            limit=limit or 10000
        )

        if not documents:
            logger.info("✓ All documents already have embeddings! Nothing to do.")
            return

        total_docs = len(documents)
        logger.info(f"Found {total_docs} documents to index")

        # Process documents in batches
        success_count = 0
        error_count = 0

        # Use tqdm for progress bar
        with tqdm(total=total_docs, desc="Indexing documents") as pbar:
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]

                # Extract texts for batch embedding
                texts = [doc.formatted_note for doc in batch]

                try:
                    # Generate embeddings for batch
                    embeddings = embedding_service.create_embeddings_batch(texts)

                    # Update each document
                    for doc, embedding in zip(batch, embeddings):
                        try:
                            doc.embedding = embedding
                            db.add(doc)
                            success_count += 1
                        except Exception as e:
                            logger.error(f"Error updating document {doc.id}: {e}")
                            error_count += 1

                    # Commit batch
                    db.commit()
                    logger.debug(f"Committed batch {i//batch_size + 1}")

                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    db.rollback()
                    error_count += len(batch)

                pbar.update(len(batch))

        # Print summary
        logger.info("=" * 60)
        logger.info("Indexing complete!")
        logger.info(f"✓ Success: {success_count} documents")
        if error_count > 0:
            logger.warning(f"✗ Errors: {error_count} documents")
        logger.info("=" * 60)

        # Print statistics by course
        print_course_statistics(db)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        db.rollback()
        raise

    finally:
        db.close()


def print_course_statistics(db):
    """Print embedding statistics grouped by course"""
    from models.course import Course

    logger.info("\nEmbedding statistics by course:")
    logger.info("-" * 60)

    courses = db.query(Course).filter(Course.status == 'active').all()

    vector_store = get_vector_store()

    for course in courses:
        stats = vector_store.get_course_document_count(db, course.id)

        if stats['total'] > 0:
            completion_pct = (stats['with_embeddings'] / stats['total']) * 100
            logger.info(
                f"{course.name:30} | "
                f"Total: {stats['total']:3} | "
                f"Indexed: {stats['with_embeddings']:3} | "
                f"Pending: {stats['without_embeddings']:3} | "
                f"Progress: {completion_pct:5.1f}%"
            )

    logger.info("-" * 60)


def verify_setup():
    """Verify that pgvector and required services are set up correctly"""
    logger.info("Verifying setup...")

    db = SessionLocal()

    try:
        # Check if pgvector extension is enabled
        result = db.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        if not result.fetchone():
            logger.error("✗ pgvector extension is not enabled!")
            logger.error("  Run: CREATE EXTENSION vector;")
            return False

        logger.info("✓ pgvector extension enabled")

        # Check if embedding column exists
        result = db.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'documents' AND column_name = 'embedding'
        """)
        if not result.fetchone():
            logger.error("✗ embedding column does not exist!")
            logger.error("  Run the migration: psql $DATABASE_URL -f migrations/002_add_vector_embeddings.sql")
            return False

        logger.info("✓ embedding column exists")

        # Test embedding service
        embedding_service = get_embedding_service()
        test_embedding = embedding_service.create_embedding("test text")
        if len(test_embedding) != 384:
            logger.error(f"✗ embedding service returned wrong dimension: {len(test_embedding)}")
            return False

        logger.info(f"✓ embedding service working (dim={len(test_embedding)})")

        return True

    except Exception as e:
        logger.error(f"✗ Setup verification failed: {e}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Index existing notes with vector embeddings")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of documents to process in each batch (default: 10)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of documents to process (default: all)"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify setup without indexing"
    )

    args = parser.parse_args()

    # Verify setup first
    if not verify_setup():
        logger.error("\nSetup verification failed. Please fix the issues above.")
        sys.exit(1)

    if args.verify_only:
        logger.info("\n✓ Setup verification complete!")
        sys.exit(0)

    # Run indexing
    try:
        index_existing_notes(batch_size=args.batch_size, limit=args.limit)
    except KeyboardInterrupt:
        logger.warning("\nIndexing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nIndexing failed: {e}")
        sys.exit(1)
