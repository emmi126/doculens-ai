"""User schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """User profile response"""
    id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update request"""
    name: Optional[str] = None
