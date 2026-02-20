from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.config import get_db
from app.core.security import get_current_user, TokenData
from app.schemas.schemas import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService
from app.models.models import User

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["comments"])


async def get_current_user_model(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user model with role."""
    from app.services.user_service import UserService
    service = UserService(db)
    user = await service.get_user(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: UUID,
    comment_create: CommentCreate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Create a new comment."""
    service = CommentService(db)
    return await service.create_comment(comment_create, task_id, current_user.id)


@router.get("", response_model=List[CommentResponse])
async def get_comments(
    task_id: UUID,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get all comments for a task."""
    service = CommentService(db)
    return await service.get_task_comments(task_id)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    task_id: UUID,
    comment_id: UUID,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Update a comment."""
    service = CommentService(db)
    return await service.update_comment(
        comment_id, comment_update, current_user.id, current_user.role
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    task_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment."""
    service = CommentService(db)
    success = await service.delete_comment(comment_id, current_user.id, current_user.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
