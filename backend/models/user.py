"""User model"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class User(Base):
    """User model for authentication and profile data"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(512))
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def get_or_create_from_auth0(cls, db, auth0_user):
        """Get existing user or create new one from Auth0 user info"""
        user = db.query(cls).filter(cls.auth0_user_id == auth0_user['sub']).first()

        if not user:
            user = cls(
                auth0_user_id=auth0_user['sub'],
                email=auth0_user.get('email'),
                name=auth0_user.get('name') or auth0_user.get('email'),
                avatar_url=auth0_user.get('picture'),
                email_verified=auth0_user.get('email_verified', False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user
