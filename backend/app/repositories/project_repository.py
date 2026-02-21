from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.base import BaseRepository
from app.models.models import Project
from typing import Optional, Tuple, List


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Project)

    async def get_with_tasks(self, project_id: str) -> Optional[Project]:
        """Get a project by ID with tasks eagerly loaded."""
        statement = (
            select(self.model)
            .where(self.model.id == project_id)
            .options(selectinload(self.model.tasks))
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_projects(
        self, user_id: any, skip: int = 0, limit: int = 100, is_admin: bool = False
    ) -> Tuple[List[Project], int]:
        """Get paginated projects. Admins see all; regular users see only their own."""
        if is_admin:
            count_stmt = select(func.count()).select_from(self.model)
            count_result = await self.db.execute(count_stmt)
            total = count_result.scalar_one()

            statement = (
                select(self.model)
                .offset(skip)
                .limit(limit)
            )
        else:
            base_where = self.model.created_by == user_id

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
        projects = list(result.scalars().all())
        return projects, total
