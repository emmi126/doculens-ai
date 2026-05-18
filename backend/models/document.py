"""Document model"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from database import Base


class Document(Base):
    """Document model for storing processed notes"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    original_text = Column(Text, nullable=False)
    formatted_note = Column(Text, nullable=False)
    excerpt = Column(String(200))
    image_path = Column(String(512))
    status = Column(String(20), default='active')
    processing_time = Column(Float)
    doc_metadata = Column(JSONB, default={}, name='metadata')  # Column name 'metadata', property 'doc_metadata'
    embedding = Column(Vector(384))  # 384-dimensional vector for semantic search
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('active', 'trash')", name='documents_status_check'),
    )

    # Relationships
    course = relationship("Course", back_populates="documents")
    user = relationship("User", back_populates="documents")
