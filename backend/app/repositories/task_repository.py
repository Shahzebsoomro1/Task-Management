from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from app.db.base import BaseRepository
from app.models.models import Task, TaskStatus, TaskPriority
from typing import Optional, List


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Task)

    async def get_project_tasks(
        self,
        project_id: str,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[str] = None,
        user_id: Optional[str] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Task], int]:
        """Get tasks for a project with filtering.
        If user_id is provided, returns tasks created by OR assigned to that user.
        """
        conditions = [self.model.project_id == project_id]

        if status:
            conditions.append(self.model.status == status)

        if user_id:
            # Show tasks the user created or is assigned to
            conditions.append(
                or_(self.model.created_by == user_id, self.model.assigned_to == user_id)
            )
        elif assigned_to:
            conditions.append(self.model.assigned_to == assigned_to)

        where_clause = and_(*conditions)

        count_stmt = select(func.count()).select_from(self.model).where(where_clause)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = select(self.model).where(where_clause)
        if order_by and hasattr(self.model, order_by):
            field = getattr(self.model, order_by)
            stmt = stmt.order_by(desc(field) if order_desc else asc(field))
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_user_assigned_tasks(self, user_id: str) -> List[Task]:
        """Get all tasks assigned to a user."""
        statement = select(self.model).where(self.model.assigned_to == user_id)
        result = await self.db.execute(statement)
        return result.scalars().all()
