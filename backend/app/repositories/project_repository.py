from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import BaseRepository
from app.models.models import Project
from typing import Optional


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Project)

    async def get_user_projects(self, user_id: any) -> list[Project]:
        """Get all projects created by a user."""
        statement = select(self.model).where(self.model.created_by == user_id)
        result = await self.db.execute(statement)
        return result.scalars().all()
