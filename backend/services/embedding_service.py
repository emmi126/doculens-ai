"""
Embedding service for generating vector representations of documents.
Uses sentence-transformers for multilingual text embeddings.
"""
from sentence_transformers import SentenceTransformer
import logging
import numpy as np
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton service for generating text embeddings"""

    # Model configuration
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM = 384  # Dimension of the embedding vectors
    MAX_CHUNK_LENGTH = 512  # Maximum tokens per chunk

    def __init__(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.MODEL_NAME}")
            self.model = SentenceTransformer(self.MODEL_NAME)
            logger.info(f"Embedding model loaded successfully (dim={self.EMBEDDING_DIM})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector (384 dimensions)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.EMBEDDING_DIM

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Ensure it's a list of floats
            embedding_list = embedding.tolist()

            logger.debug(f"Generated embedding for text (length={len(text)})")
            return embedding_list

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector on error
            return [0.0] * self.EMBEDDING_DIM

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch (more efficient).

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [t if t and t.strip() else " " for t in texts]

        try:
            embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * self.EMBEDDING_DIM] * len(texts)

    def chunk_text_by_headers(self, markdown_text: str) -> List[Dict[str, str]]:
        """
        Split markdown text into chunks based on headers.
        Preserves semantic structure by keeping sections together.

        Args:
            markdown_text: Markdown formatted text

        Returns:
            List of chunks with metadata
        """
        chunks = []

        # Split by markdown headers (## or ###)
        sections = re.split(r'\n(#{1,3})\s+(.+?)\n', markdown_text)

        if len(sections) == 1:
            # No headers found, treat as single chunk
            if markdown_text.strip():
                chunks.append({
                    'content': markdown_text.strip(),
                    'header': None,
                    'level': 0
                })
        else:
            current_content = sections[0].strip() if sections[0].strip() else None

            # Process header groups
            for i in range(1, len(sections), 3):
                if i + 2 <= len(sections):
                    header_marks = sections[i]
                    header_text = sections[i + 1]
                    section_content = sections[i + 2] if i + 2 < len(sections) else ""

                    # Add previous content if exists
                    if current_content:
                        chunks.append({
                            'content': current_content,
                            'header': None,
                            'level': 0
                        })

                    # Add section with header
                    full_content = f"{header_marks} {header_text}\n{section_content}".strip()
                    chunks.append({
                        'content': full_content,
                        'header': header_text,
                        'level': len(header_marks)
                    })

                    current_content = None

            # Add any remaining content
            if current_content:
                chunks.append({
                    'content': current_content,
                    'header': None,
                    'level': 0
                })

        # Filter out empty chunks and limit size
        valid_chunks = []
        for chunk in chunks:
            if chunk['content']:
                # If chunk is too long, split it further
                if len(chunk['content']) > self.MAX_CHUNK_LENGTH * 4:  # ~2000 chars
                    sub_chunks = self._split_long_chunk(chunk['content'], chunk['header'])
                    valid_chunks.extend(sub_chunks)
                else:
                    valid_chunks.append(chunk)

        logger.info(f"Split text into {len(valid_chunks)} chunks")
        return valid_chunks

    def _split_long_chunk(self, text: str, header: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Split a long chunk into smaller pieces by paragraphs.

        Args:
            text: Long text to split
            header: Header of the section (if any)

        Returns:
            List of smaller chunks
        """
        chunks = []
        paragraphs = text.split('\n\n')

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.MAX_CHUNK_LENGTH * 4:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append({
                        'content': current_chunk.strip(),
                        'header': header,
                        'level': 2 if header else 0
                    })
                current_chunk = para + "\n\n"

        # Add remaining content
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'header': header,
                'level': 2 if header else 0
            })

        return chunks

    def create_document_embedding(self, document_text: str, use_chunking: bool = False) -> List[float]:
        """
        Create embedding for an entire document.

        Args:
            document_text: Full document text
            use_chunking: If True, create chunks and average their embeddings

        Returns:
            Single embedding vector representing the document
        """
        if not use_chunking:
            # Simple: embed the entire document
            return self.create_embedding(document_text)
        else:
            # Advanced: chunk and average embeddings
            chunks = self.chunk_text_by_headers(document_text)

            if not chunks:
                return [0.0] * self.EMBEDDING_DIM

            # Get embeddings for all chunks
            chunk_texts = [c['content'] for c in chunks]
            embeddings = self.create_embeddings_batch(chunk_texts)

            # Average the embeddings
            avg_embedding = np.mean(embeddings, axis=0)
            return avg_embedding.tolist()


# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
