import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.config import get_db
from app.db.database import Base
from app.models.models import User, Project, Task, Comment, UserRole, TaskStatus, TaskPriority
from app.core.security import get_password_hash
from uuid import uuid4


DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create a test database."""
    engine = create_async_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False})
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def get_test_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = get_test_db
    
    yield async_session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    async with test_db() as session:
        user = User(
            id=uuid4(),
            name="Test User",
            email="test@example.com",
            password_hash=get_password_hash("testpass123"),
            role=UserRole.user,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
async def test_admin(test_db):
    """Create a test admin user."""
    async with test_db() as session:
        admin = User(
            id=uuid4(),
            name="Test Admin",
            email="admin@example.com",
            password_hash=get_password_hash("adminpass123"),
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin


class TestAuth:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register(self, client):
        """Test user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "securepass123",
                "role": "user",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "name": "Another User",
                "email": "test@example.com",
                "password": "securepass123",
                "role": "user",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login(self, client, test_user):
        """Test user login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401


class TestProjects:
    """Test project endpoints."""

    @pytest.mark.asyncio
    async def test_create_project(self, client, test_user):
        """Test creating a project."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        token = login_response.json()["access_token"]

        # Create project
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "description": "A test project",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"

    @pytest.mark.asyncio
    async def test_get_projects(self, client, test_user):
        """Test getting projects."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTasks:
    """Test task endpoints."""

    @pytest.mark.asyncio
    async def test_create_task(self, client, test_user, test_db):
        """Test creating a task."""
        # Create a project first
        async with test_db() as session:
            project = Project(
                id=uuid4(),
                name="Test Project",
                created_by=test_user.id,
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            project_id = project.id

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        token = login_response.json()["access_token"]

        response = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={
                "title": "Test Task",
                "description": "A test task",
                "priority": "high",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"


class TestHealth:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
