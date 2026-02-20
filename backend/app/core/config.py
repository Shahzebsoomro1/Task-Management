from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./taskmanagement.db"
    SECRET_KEY: str = "your-secret-key-change-in-production-at-least-32-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    APP_NAME: str = "Task Management System"
    SQLALCHEMY_ECHO: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        yield session
