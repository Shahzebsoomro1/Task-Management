from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import BaseRepository
from app.models.models import User
from typing import Optional


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(self.model).where(self.model.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
