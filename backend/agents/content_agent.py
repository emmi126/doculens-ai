"""
Content Agent for Multi-Agent Note Processing System

Responsibilities:
1. Integrate RAG retrieval for historical context
2. Optimize and enhance content with context
3. Add cross-references to related notes
4. Supplement context where needed

Input: ocr_corrected_text, key_concepts, course_id
Output: related_notes, rag_context, enhanced_content, cross_references
"""

import time
import logging
import json
import re
from typing import List, Dict, Optional
from uuid import UUID

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from .state import (
    NoteProcessingState,
    AgentOutput,
    RelatedNote,
    ProcessingStatus
)
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store
from database import SessionLocal
from config import settings

logger = logging.getLogger(__name__)


llm = ChatAnthropic(
    model=settings.anthropic_model,
    api_key=settings.anthropic_api_key,
    temperature=0.3,
    max_tokens=4096
)


CONTENT_ENHANCEMENT_PROMPT = """You are a note-content enhancement specialist. Improve a new note using relevant historical notes from the same course.

You will receive corrected OCR text, extracted key concepts, and optional related notes.

Requirements:
1. Identify genuine conceptual connections and continuations.
2. Add only context supported by the supplied notes; do not introduce external knowledge.
3. Create cross-references only when they materially help understanding.
4. Keep the new note independent and do not copy large passages from historical notes.
5. Preserve the source language and do not translate by default.

**Output format (JSON)**:
```json
{
    "enhanced_content": "enhanced note in Markdown",
    "cross_references": [
        {
            "concept": "concept name",
            "reference_title": "referenced note title",
            "relationship": "relationship description",
            "position": "location in the new note"
        }
    ],
    "new_concepts": ["new concept"],
    "reviewed_concepts": ["reviewed concept"]
}
```

Return valid JSON only."""


def format_rag_context(related_notes: List[RelatedNote]) -> str:
    """
    Format related notes into a context string for the LLM prompt.
    """
    if not related_notes:
        return ""

    context_parts = []
    for i, note in enumerate(related_notes, 1):
        similarity_pct = int(note.similarity * 100)
        context_parts.append(
            f"### Historical note {i}: {note.title}\n"
            f"*Similarity: {similarity_pct}% | Date: {note.created_at or 'Unknown'}*\n\n"
            f"{note.excerpt[:500]}...\n\n---"
        )

    return "\n\n".join(context_parts)


def format_key_concepts(key_concepts: list) -> str:
    """Format key concepts for the LLM prompt."""
    if not key_concepts:
        return "No key concepts were identified."

    concepts = []
    for concept in key_concepts[:10]:  # Limit to 10 concepts
        term = getattr(concept, 'term', str(concept))
        definition = getattr(concept, 'definition', None)
        if definition:
            concepts.append(f"- **{term}**: {definition}")
        else:
            concepts.append(f"- **{term}**")

    return "\n".join(concepts)


async def content_agent(state: NoteProcessingState) -> NoteProcessingState:
    """
    Content Agent: Enhances note content with RAG integration.

    This agent:
    1. Checks if RAG should be used (based on course_id)
    2. Generates embeddings for the text
    3. Retrieves similar documents from vector store
    4. Enhances content with historical context
    5. Creates cross-references

    Args:
        state: Current processing state

    Returns:
        Updated state with enhanced content
    """
    start_time = time.time()
    agent_name = "content_agent"

    logger.info(f"[{agent_name}] Starting content enhancement...")

    state["current_agent"] = agent_name

    # Check if previous agents succeeded
    structure_output = state.get("structure_agent_output")
    if structure_output and not structure_output.success:
        # If structure agent failed, we can still try to enhance
        logger.warning(f"[{agent_name}] Structure agent failed, continuing with basic content")

    try:
        text = state.get("ocr_corrected_text", "")
        if not text:
            raise ValueError("No text available for content enhancement")

        course_id = state.get("course_id")
        should_use_rag = state.get("should_use_rag", False) and course_id is not None

        # Initialize empty related notes
        state["related_notes"] = []
        state["rag_context"] = None
        state["cross_references"] = []

        # Step 1: RAG Retrieval (if applicable)
        if should_use_rag:
            try:
                logger.info(f"[{agent_name}] Performing RAG retrieval for course {course_id}")

                # Get embedding for the new text
                embedding_service = get_embedding_service()
                text_embedding = embedding_service.create_embedding(text)

                # Query vector store for similar documents
                vector_store = get_vector_store()
                db = SessionLocal()

                try:
                    similar_docs = vector_store.find_similar_documents(
                        db=db,
                        query_embedding=text_embedding,
                        course_id=UUID(course_id),
                        top_k=3,
                        similarity_threshold=0.4
                    )

                    # Convert to RelatedNote objects
                    related_notes = []
                    for doc, similarity in similar_docs:
                        related_notes.append(RelatedNote(
                            document_id=str(doc.id),
                            title=doc.title,
                            excerpt=doc.formatted_note[:500] if doc.formatted_note else "",
                            similarity=similarity,
                            created_at=doc.created_at.strftime('%Y-%m-%d') if doc.created_at else None
                        ))

                    state["related_notes"] = related_notes
                    state["rag_context"] = format_rag_context(related_notes)

                    logger.info(f"[{agent_name}] Found {len(related_notes)} related notes")

                finally:
                    db.close()

            except Exception as rag_error:
                logger.warning(f"[{agent_name}] RAG retrieval failed: {rag_error}. Continuing without context.")

        # Step 2: Content Enhancement with LLM
        key_concepts = state.get("key_concepts", [])
        rag_context = state.get("rag_context", "")

        if rag_context or key_concepts:
            try:
                # Build prompt for content enhancement
                user_content = f"""**New note OCR text**:
```
{text}
```

**Extracted key concepts**:
{format_key_concepts(key_concepts)}
"""
                if rag_context:
                    user_content += f"""

**Related historical notes**:
{rag_context}
"""

                user_content += """

Enhance the new note using the information above. Return JSON."""

                messages = [
                    SystemMessage(content=CONTENT_ENHANCEMENT_PROMPT),
                    HumanMessage(content=user_content)
                ]

                response = await llm.ainvoke(messages)

                # Parse response
                response_text = response.content
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text.strip()

                try:
                    data = json.loads(json_str)
                    state["enhanced_content"] = data.get("enhanced_content", text)
                    state["cross_references"] = data.get("cross_references", [])

                    logger.info(
                        f"[{agent_name}] Content enhanced with "
                        f"{len(data.get('cross_references', []))} cross-references"
                    )

                except json.JSONDecodeError:
                    logger.warning(f"[{agent_name}] Failed to parse LLM response, using original text")
                    state["enhanced_content"] = text

            except Exception as llm_error:
                logger.warning(f"[{agent_name}] LLM enhancement failed: {llm_error}")
                state["enhanced_content"] = text

        else:
            # No RAG context or concepts, use original text
            state["enhanced_content"] = text
            logger.info(f"[{agent_name}] No context available, using original text")

        # Record success
        processing_time = time.time() - start_time
        state["processing_times"][agent_name] = processing_time
        state["content_agent_output"] = AgentOutput(
            success=True,
            data={
                "related_notes_count": len(state["related_notes"]),
                "cross_references_count": len(state["cross_references"]),
                "used_rag": should_use_rag and len(state["related_notes"]) > 0
            },
            processing_time=processing_time,
            agent_name=agent_name
        )

        logger.info(
            f"[{agent_name}] Completed in {processing_time:.2f}s. "
            f"RAG used: {should_use_rag}, "
            f"Related notes: {len(state['related_notes'])}"
        )

    except Exception as e:
        error_msg = f"Content Agent failed: {str(e)}"
        logger.error(f"[{agent_name}] {error_msg}")

        state["errors"].append(error_msg)
        state["enhanced_content"] = state.get("ocr_corrected_text", "")
        state["content_agent_output"] = AgentOutput(
            success=False,
            data=None,
            error=error_msg,
            processing_time=time.time() - start_time,
            agent_name=agent_name
        )

    return state
