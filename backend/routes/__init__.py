"""API routes"""
from .user import router as user_router
from .courses import router as courses_router
from .documents import router as documents_router

__all__ = ["user_router", "courses_router", "documents_router"]
