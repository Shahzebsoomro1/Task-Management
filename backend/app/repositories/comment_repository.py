from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import BaseRepository
from app.models.models import Comment
from typing import List
from uuid import UUID


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Comment)

    async def get_task_comments(self, task_id: UUID) -> List[Comment]:
        """Get all comments for a task."""
        statement = select(self.model).where(self.model.task_id == task_id)
        result = await self.db.execute(statement)
        return result.scalars().all()
