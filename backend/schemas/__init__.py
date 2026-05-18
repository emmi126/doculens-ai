"""Pydantic schemas for request/response validation"""
from .common import (
    HealthResponse,
    UploadResponse,
    OCRResponse,
    ProcessNoteRequest,
    ProcessNoteResponse,
    QAItemResponse,
    KnowledgeCardResponse,
    RelatedNoteResponse,
    MultiAgentMetadata,
    MultiAgentProcessNoteResponse,
)
from .user import UserResponse, UserUpdate
from .course import CourseCreate, CourseUpdate, CourseResponse
from .document import DocumentCreate, DocumentUpdate, DocumentResponse

__all__ = [
    "HealthResponse",
    "UploadResponse",
    "OCRResponse",
    "ProcessNoteRequest",
    "ProcessNoteResponse",
    "QAItemResponse",
    "KnowledgeCardResponse",
    "RelatedNoteResponse",
    "MultiAgentMetadata",
    "MultiAgentProcessNoteResponse",
    "UserResponse",
    "UserUpdate",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
]
