from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.comment_repository import CommentRepository
from app.schemas.schemas import CommentCreate, CommentUpdate, CommentResponse
from app.models.models import Comment, UserRole
from fastapi import HTTPException, status
from typing import Optional, List


class CommentService:
    """Service for comment operations."""

    def __init__(self, db: AsyncSession):
        self.repository = CommentRepository(db)

    async def create_comment(
        self, comment_create: CommentCreate, task_id: str, user_id: str
    ) -> CommentResponse:
        """Create a new comment."""
        comment = Comment(
            content=comment_create.content,
            task_id=str(task_id),
            created_by=str(user_id),
        )
        self.repository.db.add(comment)
        await self.repository.db.commit()
        await self.repository.db.refresh(comment)
        return CommentResponse.model_validate(comment)

    async def get_comment(self, comment_id: str, user_id: str, user_role: UserRole) -> Optional[Comment]:
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

    async def get_task_comments(self, task_id: str, skip: int = 0, limit: int = 100):
        """Get paginated comments for a task. Returns (comments, total)."""
        return await self.repository.get_task_comments(task_id, skip=skip, limit=limit)

    async def update_comment(
        self, comment_id: str, comment_update: CommentUpdate, user_id: str, user_role: UserRole
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
        self, comment_id: str, user_id: str, user_role: UserRole
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
