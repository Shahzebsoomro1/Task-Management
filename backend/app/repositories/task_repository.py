from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.base import BaseRepository
from app.models.models import Task, TaskStatus, TaskPriority
from typing import Optional, List
from uuid import UUID


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Task)

    async def get_project_tasks(
        self,
        project_id: UUID,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[UUID] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Task], int]:
        """Get tasks for a project with filtering."""
        filters = {"project_id": project_id}
        if status:
            filters["status"] = status
        if assigned_to:
            filters["assigned_to"] = assigned_to

        return await self.get_multi(
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )

    async def get_user_assigned_tasks(self, user_id: UUID) -> List[Task]:
        """Get all tasks assigned to a user."""
        statement = select(self.model).where(self.model.assigned_to == user_id)
        result = await self.db.execute(statement)
        return result.scalars().all()
