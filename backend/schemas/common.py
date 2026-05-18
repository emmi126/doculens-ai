"""Common schemas for existing endpoints"""
from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    message: str


class UploadResponse(BaseModel):
    filename: str
    message: str
    file_path: str


class OCRResponse(BaseModel):
    success: bool
    text: str
    confidence: Optional[float] = None
    error: Optional[str] = None


class ProcessNoteRequest(BaseModel):
    # Can be extended with course_id
    course_id: Optional[str] = None
    additional_context: Optional[str] = None


class ProcessNoteResponse(BaseModel):
    success: bool
    original_text: str  # OCR extracted text
    formatted_note: str  # LLM formatted note
    processing_time: float
    document_id: Optional[str] = None  # ID if saved to database
    error: Optional[str] = None


class QAItemResponse(BaseModel):
    """Single Q&A item from multi-agent processing"""
    question: str
    answer: str
    difficulty: str = "medium"
    concept: Optional[str] = None


class KnowledgeCardResponse(BaseModel):
    """Knowledge card from multi-agent processing"""
    front: str
    back: str
    tags: list[str] = []
    concept: Optional[str] = None


class RelatedNoteResponse(BaseModel):
    """Related note from RAG retrieval"""
    document_id: str
    title: str
    excerpt: str
    similarity: float
    created_at: Optional[str] = None


class MultiAgentMetadata(BaseModel):
    """Metadata from multi-agent processing"""
    processing_time_total: float
    processing_times: dict[str, float]
    ocr_confidence: float
    document_type: str
    related_notes_count: int
    key_concepts_count: int
    qa_items_count: int
    knowledge_cards_count: int
    special_contents_count: int
    errors: list[str]
    agents_run: list[str]
    used_rag: bool
    generated_qa: bool
    timestamp: str


class MultiAgentProcessNoteResponse(BaseModel):
    """Response from multi-agent note processing endpoint"""
    success: bool
    # Main outputs
    original_text: str
    corrected_text: str
    final_note: str
    # Q&A materials
    qa_items: list[QAItemResponse] = []
    knowledge_cards: list[KnowledgeCardResponse] = []
    key_points: list[str] = []
    # Related notes from RAG
    related_notes: list[RelatedNoteResponse] = []
    # Key concepts extracted
    key_concepts: list[dict] = []
    # Processing metadata
    metadata: Optional[MultiAgentMetadata] = None
    # Document ID if saved
    document_id: Optional[str] = None
    # Error if failed
    error: Optional[str] = None
