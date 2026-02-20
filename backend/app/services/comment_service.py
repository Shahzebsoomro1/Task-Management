from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.comment_repository import CommentRepository
from app.schemas.schemas import CommentCreate, CommentUpdate, CommentResponse
from app.models.models import Comment, UserRole
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional, List


class CommentService:
    """Service for comment operations."""

    def __init__(self, db: AsyncSession):
        self.repository = CommentRepository(db)

    async def create_comment(
        self, comment_create: CommentCreate, task_id: UUID, user_id: UUID
    ) -> CommentResponse:
        """Create a new comment."""
        comment = await self.repository.create(comment_create)
        comment.task_id = task_id
        comment.created_by = user_id
        await self.repository.db.commit()
        await self.repository.db.refresh(comment)
        return CommentResponse.model_validate(comment)

    async def get_comment(self, comment_id: UUID, user_id: UUID, user_role: UserRole) -> Optional[Comment]:
        """Get a comment by ID."""
        comment = await self.repository.get(comment_id)
        if not comment:
            return None

        # Check authorization
        if user_role != UserRole.admin and comment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this comment",
            )
        return comment

    async def get_task_comments(self, task_id: UUID) -> List[Comment]:
        """Get all comments for a task."""
        return await self.repository.get_task_comments(task_id)

    async def update_comment(
        self, comment_id: UUID, comment_update: CommentUpdate, user_id: UUID, user_role: UserRole
    ) -> CommentResponse:
        """Update a comment."""
        comment = await self.get_comment(comment_id, user_id, user_role)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        # Check authorization
        if user_role != UserRole.admin and comment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment",
            )

        comment = await self.repository.update(comment, comment_update)
        return CommentResponse.model_validate(comment)

    async def delete_comment(
        self, comment_id: UUID, user_id: UUID, user_role: UserRole
    ) -> bool:
        """Delete a comment."""
        comment = await self.get_comment(comment_id, user_id, user_role)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )

        # Check authorization
        if user_role != UserRole.admin and comment.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment",
            )

        return await self.repository.delete_by_id(comment_id)
