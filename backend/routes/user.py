"""User profile routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from services.auth_service import get_current_user
from schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at
    )


@router.put("/", response_model=dict)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if user_update.name:
        current_user.name = user_update.name

    db.commit()

    return {"message": "Profile updated"}
