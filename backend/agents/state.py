"""
State Schema for Multi-Agent Note Processing System

Defines the shared state that flows through all agents in the LangGraph workflow.
Each agent reads from and writes to specific fields in this state.
"""

from typing import TypedDict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class ProcessingStatus(str, Enum):
    """Status of the overall processing pipeline."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SpecialContent:
    """Represents special content identified in the note (formulas, diagrams, etc.)."""
    content_type: str  # "formula", "diagram", "code", "table"
    raw_text: str
    processed_text: str
    position: int  # Character position in original text
    confidence: float = 1.0


@dataclass
class TextBlock:
    """A structured block of text with semantic information."""
    content: str
    block_type: str  # "title", "heading", "paragraph", "list", "code"
    level: int = 0  # Heading level (1-6) or list nesting depth
    metadata: dict = field(default_factory=dict)


@dataclass
class KeyConcept:
    """A key concept extracted from the note."""
    term: str
    definition: Optional[str] = None
    context: Optional[str] = None
    importance: float = 1.0  # 0.0 to 1.0


@dataclass
class RelatedNote:
    """Reference to a related historical note from RAG."""
    document_id: str
    title: str
    excerpt: str
    similarity: float
    created_at: Optional[str] = None


@dataclass
class QAItem:
    """A question-answer pair for review."""
    question: str
    answer: str
    difficulty: str = "medium"  # "easy", "medium", "hard"
    concept: Optional[str] = None  # Related concept


@dataclass
class KnowledgeCard:
    """A flashcard-style knowledge card."""
    front: str  # Question or term
    back: str   # Answer or definition
    tags: List[str] = field(default_factory=list)
    concept: Optional[str] = None


@dataclass
class AgentOutput:
    """Standard output from each agent."""
    success: bool
    data: Any
    error: Optional[str] = None
    processing_time: float = 0.0
    agent_name: str = ""


class NoteProcessingState(TypedDict, total=False):
    """
    Shared state for the multi-agent note processing workflow.

    This TypedDict defines all fields that flow through the LangGraph.
    Each agent reads and writes to specific fields.

    Flow:
        Start → OCR Agent → Structure Agent → Content Agent → QA Agent → Integration Agent → End
    """

    # === Input Fields ===
    image_bytes: bytes  # Raw image data
    course_id: Optional[str]  # Course ID for RAG context
    course_name: Optional[str]  # Course name for context
    additional_context: Optional[str]  # User-provided context
    user_id: Optional[str]  # User ID for database operations

    # === OCR Agent Output ===
    ocr_raw_text: str  # Raw OCR output before correction
    ocr_corrected_text: str  # LLM-corrected OCR text
    ocr_confidence: float  # OCR confidence score (0.0-1.0)
    special_contents: List[SpecialContent]  # Formulas, diagrams, etc.
    ocr_agent_output: AgentOutput

    # === Structure Agent Output ===
    text_blocks: List[TextBlock]  # Parsed text structure
    heading_hierarchy: List[dict]  # Heading tree structure
    key_concepts: List[KeyConcept]  # Extracted concepts
    document_type: str  # "lecture", "notes", "textbook", etc.
    structure_agent_output: AgentOutput

    # === Content Agent Output ===
    related_notes: List[RelatedNote]  # RAG-retrieved notes
    rag_context: Optional[str]  # Formatted RAG context for LLM
    enhanced_content: str  # Content with RAG integration
    cross_references: List[dict]  # References to historical notes
    content_agent_output: AgentOutput

    # === QA Agent Output ===
    qa_items: List[QAItem]  # Review questions
    knowledge_cards: List[KnowledgeCard]  # Flashcards
    key_points: List[str]  # Highlighted key points
    qa_agent_output: AgentOutput

    # === Integration Agent Output ===
    final_note: str  # Final formatted Markdown note
    final_metadata: dict  # Processing metadata
    integration_agent_output: AgentOutput

    # === Control Fields ===
    status: ProcessingStatus
    current_agent: str
    errors: List[str]
    processing_times: dict  # Agent name -> processing time
    should_use_rag: bool  # Whether to use RAG (based on course_id)
    should_generate_qa: bool  # Whether to generate Q&A (configurable)


def create_initial_state(
    image_bytes: bytes,
    course_id: Optional[str] = None,
    course_name: Optional[str] = None,
    additional_context: Optional[str] = None,
    user_id: Optional[str] = None,
    generate_qa: bool = True
) -> NoteProcessingState:
    """
    Create the initial state for the multi-agent workflow.

    Args:
        image_bytes: Raw image data to process
        course_id: Optional course ID for RAG context
        course_name: Optional course name
        additional_context: Optional user-provided context
        user_id: Optional user ID for database operations
        generate_qa: Whether to generate Q&A items

    Returns:
        Initial NoteProcessingState ready for the workflow
    """
    return NoteProcessingState(
        # Input
        image_bytes=image_bytes,
        course_id=course_id,
        course_name=course_name,
        additional_context=additional_context,
        user_id=user_id,

        # OCR Agent
        ocr_raw_text="",
        ocr_corrected_text="",
        ocr_confidence=0.0,
        special_contents=[],

        # Structure Agent
        text_blocks=[],
        heading_hierarchy=[],
        key_concepts=[],
        document_type="notes",

        # Content Agent
        related_notes=[],
        rag_context=None,
        enhanced_content="",
        cross_references=[],

        # QA Agent
        qa_items=[],
        knowledge_cards=[],
        key_points=[],

        # Integration Agent
        final_note="",
        final_metadata={},

        # Control
        status=ProcessingStatus.PENDING,
        current_agent="",
        errors=[],
        processing_times={},
        should_use_rag=course_id is not None,
        should_generate_qa=generate_qa,
    )
