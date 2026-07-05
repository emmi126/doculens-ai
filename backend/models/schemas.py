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
    # Extend this request with fields such as course information when needed.
    additional_context: Optional[str] = None

class ProcessNoteResponse(BaseModel):
    success: bool
    original_text: str  # Raw text recognized by OCR.
    formatted_note: str  # Note formatted by the LLM.
    processing_time: float
    document_id: Optional[str] = None  # ID of saved document (for fetching related notes)
    error: Optional[str] = None
