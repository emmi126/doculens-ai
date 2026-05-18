"""Document schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentCreate(BaseModel):
    """Document creation request"""
    course_id: str
    title: str = Field(..., min_length=1, max_length=500)
    original_text: str
    formatted_note: str
    excerpt: Optional[str] = Field(None, max_length=200)
    image_path: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """Document update request"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    formatted_note: Optional[str] = None
    course_id: Optional[str] = None  # For moving documents


class DocumentResponse(BaseModel):
    """Document response"""
    id: str
    course_id: str
    title: str
    original_text: str
    formatted_note: str
    excerpt: Optional[str] = None
    image_path: Optional[str] = None
    status: str
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
