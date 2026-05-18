"""Course routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Course, User
from services.auth_service import get_current_user
from schemas.course import CourseCreate, CourseUpdate, CourseResponse

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    status: str = 'active',
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all courses for authenticated user"""
    courses = db.query(Course).filter(
        Course.user_id == current_user.id,
        Course.status == status
    ).order_by(Course.updated_at.desc()).all()

    return [
        CourseResponse(
            id=str(course.id),
            name=course.name,
            description=course.description,
            color=course.color,
            icon=course.icon,
            document_count=course.document_count,
            status=course.status,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        for course in courses
    ]


@router.post("/", response_model=dict)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new course"""
    course = Course(
        user_id=current_user.id,
        name=course_data.name,
        description=course_data.description,
        color=course_data.color,
        icon=course_data.icon
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return {"id": str(course.id), "name": course.name}


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific course"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return CourseResponse(
        id=str(course.id),
        name=course.name,
        description=course.description,
        color=course.color,
        icon=course.icon,
        document_count=course.document_count,
        status=course.status,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a course"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update fields if provided
    if course_data.name is not None:
        course.name = course_data.name
    if course_data.description is not None:
        course.description = course_data.description
    if course_data.color is not None:
        course.color = course_data.color
    if course_data.icon is not None:
        course.icon = course_data.icon

    course.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Course updated"}


@router.delete("/{course_id}", response_model=dict)
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move course to trash"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Soft delete
    course.status = 'trash'
    course.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Course moved to trash"}


@router.post("/{course_id}/restore", response_model=dict)
async def restore_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore course from trash"""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id,
        Course.status == 'trash'
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found in trash")

    course.status = 'active'
    course.deleted_at = None
    db.commit()

    return {"message": "Course restored"}
