from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.base import BaseRepository
from app.models.models import Comment
from typing import List, Tuple


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Comment)

    async def get_task_comments(
        self, task_id: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Comment], int]:
        """Get paginated comments for a task."""
        base_where = self.model.task_id == task_id

        count_stmt = select(func.count()).select_from(self.model).where(base_where)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        statement = (
            select(self.model)
            .where(base_where)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(statement)
        comments = list(result.scalars().all())
        return comments, total
