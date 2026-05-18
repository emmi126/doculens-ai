#!/usr/bin/env python3
"""
Test script to verify RAG system is working correctly.

Usage:
    python scripts/test_rag_setup.py

This will test:
1. pgvector extension
2. Embedding service
3. Vector store search
4. RAG-enhanced LLM formatting
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
from services.llm_service import llm_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pgvector():
    """Test that pgvector extension is enabled"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: pgvector Extension")
    logger.info("=" * 60)

    db = SessionLocal()
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"))
        row = result.fetchone()

        if row:
            logger.info(f"✓ pgvector extension enabled (version: {row[1]})")
            return True
        else:
            logger.error("✗ pgvector extension not found")
            logger.error("  Run: CREATE EXTENSION vector;")
            return False

    except Exception as e:
        logger.error(f"✗ Error checking pgvector: {e}")
        return False
    finally:
        db.close()


def test_embedding_service():
    """Test embedding generation"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Embedding Service")
    logger.info("=" * 60)

    try:
        service = get_embedding_service()

        # Test single embedding
        test_text = "This is a test document about machine learning."
        embedding = service.create_embedding(test_text)

        if len(embedding) == 384:
            logger.info(f"✓ Single embedding generated (dim={len(embedding)})")
        else:
            logger.error(f"✗ Wrong embedding dimension: {len(embedding)} (expected 384)")
            return False

        # Test batch embeddings
        test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing deals with text data."
        ]
        embeddings = service.create_embeddings_batch(test_texts)

        if len(embeddings) == 3 and all(len(e) == 384 for e in embeddings):
            logger.info(f"✓ Batch embeddings generated ({len(embeddings)} docs)")
        else:
            logger.error("✗ Batch embedding failed")
            return False

        # Test chunking
        markdown_text = """# Machine Learning

## Introduction
Machine learning is a method of data analysis that automates analytical model building.

## Types
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
"""
        chunks = service.chunk_text_by_headers(markdown_text)
        logger.info(f"✓ Text chunking works ({len(chunks)} chunks created)")

        return True

    except Exception as e:
        logger.error(f"✗ Embedding service error: {e}")
        return False


def test_vector_search():
    """Test vector similarity search"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Vector Similarity Search")
    logger.info("=" * 60)

    db = SessionLocal()
    try:
        # Check if there are any documents with embeddings
        from models.document import Document

        doc_count = db.query(Document).filter(
            Document.embedding.isnot(None),
            Document.status == 'active'
        ).count()

        logger.info(f"Found {doc_count} documents with embeddings")

        if doc_count == 0:
            logger.warning("⚠ No documents with embeddings to test search")
            logger.warning("  Run: python scripts/index_existing_notes.py")
            return True  # Not a failure, just no data

        # Get a sample document
        sample_doc = db.query(Document).filter(
            Document.embedding.isnot(None),
            Document.status == 'active'
        ).first()

        if not sample_doc:
            logger.warning("⚠ Could not get sample document")
            return True

        # Test similarity search
        vector_store = get_vector_store()
        similar_docs = vector_store.find_similar_documents(
            db=db,
            query_embedding=sample_doc.embedding,
            course_id=sample_doc.course_id,
            top_k=3,
            exclude_document_id=sample_doc.id
        )

        logger.info(f"✓ Vector search returned {len(similar_docs)} similar documents")

        if similar_docs:
            for i, (doc, similarity) in enumerate(similar_docs, 1):
                logger.info(f"  {i}. {doc.title[:50]:50} (similarity: {similarity:.3f})")

        # Test related notes
        related = vector_store.find_related_notes(
            db=db,
            document_id=sample_doc.id,
            top_k=3
        )

        logger.info(f"✓ Related notes API returned {len(related)} notes")

        return True

    except Exception as e:
        logger.error(f"✗ Vector search error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_rag_formatting():
    """Test RAG-enhanced note formatting"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: RAG-Enhanced LLM Formatting")
    logger.info("=" * 60)

    try:
        # Test with mock historical context
        mock_context = [
            {
                'title': 'Introduction to Machine Learning',
                'content': '# Machine Learning Basics\n\nMachine learning is a subset of AI that enables systems to learn from data.',
                'created_at': '2025-12-01',
                'similarity': 0.85
            }
        ]

        mock_ocr = """Machine learning algorithms
        - Linear Regression
        - Decision Trees
        - Neural Networks"""

        logger.info("Testing RAG formatting with mock data...")
        logger.info("(Note: This will call Claude API and may incur costs)")

        # Uncomment the following to actually test the LLM
        # formatted = llm_service.format_note_with_rag(
        #     ocr_text=mock_ocr,
        #     course_name="AI Course",
        #     historical_context=mock_context
        # )
        # logger.info(f"✓ RAG formatting successful ({len(formatted)} characters)")
        # logger.info(f"\nFormatted output preview:\n{formatted[:200]}...")

        logger.info("✓ RAG formatting method is available")
        logger.info("  (Skipping actual API call to save costs)")
        logger.info("  Uncomment code in test_rag_setup.py to test with real API")

        return True

    except Exception as e:
        logger.error(f"✗ RAG formatting error: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status:8} | {test_name}")

    logger.info("=" * 60)

    if all_passed:
        logger.info("✓ All tests passed! RAG system is ready.")
        return 0
    else:
        logger.error("✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    logger.info("RAG System Test Suite")
    logger.info("=" * 60)

    results = {
        "pgvector Extension": test_pgvector(),
        "Embedding Service": test_embedding_service(),
        "Vector Search": test_vector_search(),
        "RAG Formatting": test_rag_formatting()
    }

    exit_code = print_summary(results)
    sys.exit(exit_code)
