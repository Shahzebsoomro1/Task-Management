from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password
from app.models.models import User
from fastapi import HTTPException, status
from typing import Optional


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.repository.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        password_hash = get_password_hash(user_create.password)

        # Create user - build User model directly since schema has 'password' but model has 'password_hash'
        user = User(
            name=user_create.name,
            email=user_create.email,
            password_hash=password_hash,
            role=user_create.role,
        )
        self.repository.db.add(user)
        await self.repository.db.commit()
        await self.repository.db.refresh(user)
        return UserResponse.model_validate(user)

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user."""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return await self.repository.get(user_id)
