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
    # 可以扩展，比如添加课程信息
    additional_context: Optional[str] = None

class ProcessNoteResponse(BaseModel):
    success: bool
    original_text: str  # OCR 识别的原始文本
    formatted_note: str  # LLM 整理后的笔记
    processing_time: float
    document_id: Optional[str] = None  # ID of saved document (for fetching related notes)
    error: Optional[str] = None