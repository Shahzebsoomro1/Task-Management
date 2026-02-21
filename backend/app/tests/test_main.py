import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.config import get_db
from app.db.database import Base
from app.models.models import User, Project, Task, Comment, UserRole, TaskStatus, TaskPriority
from app.core.security import get_password_hash
from uuid import uuid4


DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create an in-memory test database and override get_db dependency."""
    engine = create_async_engine(
        DATABASE_URL_TEST,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    yield async_session

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(test_db):
    """Create a regular test user in the DB."""
    async with test_db() as session:
        user = User(
            id=str(uuid4()),
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
    """Create an admin test user in the DB."""
    async with test_db() as session:
        admin = User(
            id=str(uuid4()),
            name="Test Admin",
            email="admin@example.com",
            password_hash=get_password_hash("adminpass123"),
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin


# ─────────────────────────── helpers ───────────────────────────

async def _login(client: AsyncClient, email: str, password: str) -> str:
    """Login and return access token."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


async def _auth_info(client: AsyncClient, email: str, password: str) -> tuple[str, str]:
    """Login and return (access_token, user_id)."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    return data["access_token"], data["user"]["id"]


async def _auth_headers(client: AsyncClient, email: str, password: str) -> dict:
    token = await _login(client, email, password)
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────── TestHealth ───────────────────────────


class TestHealth:
    """Basic health-check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ─────────────────────────── TestAuth ───────────────────────────

class TestAuth:
    """Authentication endpoints: register / login / me."""

    @pytest.mark.asyncio
    async def test_register(self, client):
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
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
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
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_me(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_me_unauthorized(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


# ─────────────────────────── TestProjects ───────────────────────────

class TestProjects:
    """Project CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_project(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Test Project", "description": "A test project"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_projects_paginated(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")

        # Create two projects
        for i in range(2):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}"},
                headers=headers,
            )

        response = await client.get("/api/v1/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert data["total"] >= 2

    @pytest.mark.asyncio
    async def test_get_projects_pagination_params(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        for i in range(3):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Proj {i}"},
                headers=headers,
            )

        response = await client.get("/api/v1/projects?skip=0&limit=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["limit"] == 2

    @pytest.mark.asyncio
    async def test_get_project_detail(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        create_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Detail Project"},
            headers=headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/projects/{project_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == project_id

    @pytest.mark.asyncio
    async def test_update_project(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        create_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Old Name"},
            headers=headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "New Name"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_delete_project(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        create_resp = await client.post(
            "/api/v1/projects",
            json={"name": "To Delete"},
            headers=headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/projects/{project_id}", headers=headers)
        assert response.status_code == 204

        get_resp = await client.get(f"/api/v1/projects/{project_id}", headers=headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_project_requires_auth(self, client):
        response = await client.get("/api/v1/projects")
        assert response.status_code == 401


# ─────────────────────────── TestTasks ───────────────────────────

class TestTasks:
    """Task CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_task(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Task Project"},
            headers=headers,
        )
        project_id = proj_resp.json()["id"]

        response = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Test Task", "description": "A test task", "priority": "high"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "todo"

    @pytest.mark.asyncio
    async def test_get_tasks_paginated(self, client, test_user):
        token, user_id = await _auth_info(client, "test@example.com", "testpass123")
        headers = {"Authorization": f"Bearer {token}"}
        proj_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Task Project 2"},
            headers=headers,
        )
        project_id = proj_resp.json()["id"]

        for i in range(3):
            await client.post(
                f"/api/v1/projects/{project_id}/tasks",
                json={"title": f"Task {i}", "assigned_to": user_id},
                headers=headers,
            )

        response = await client.get(
            f"/api/v1/projects/{project_id}/tasks",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_get_tasks_with_limit(self, client, test_user):
        token, user_id = await _auth_info(client, "test@example.com", "testpass123")
        headers = {"Authorization": f"Bearer {token}"}
        proj_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Limit Project"},
            headers=headers,
        )
        project_id = proj_resp.json()["id"]

        for i in range(5):
            await client.post(
                f"/api/v1/projects/{project_id}/tasks",
                json={"title": f"Task {i}", "assigned_to": user_id},
                headers=headers,
            )

        response = await client.get(
            f"/api/v1/projects/{project_id}/tasks?skip=0&limit=2",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_update_task_status(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects",
            json={"name": "Status Project"},
            headers=headers,
        )
        project_id = proj_resp.json()["id"]

        task_resp = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Status Task"},
            headers=headers,
        )
        task_id = task_resp.json()["id"]

        response = await client.put(
            f"/api/v1/projects/{project_id}/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_delete_task(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects", json={"name": "Del Task Proj"}, headers=headers
        )
        project_id = proj_resp.json()["id"]
        task_resp = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Delete Me"},
            headers=headers,
        )
        task_id = task_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/projects/{project_id}/tasks/{task_id}", headers=headers
        )
        assert response.status_code == 204


# ─────────────────────────── TestComments ───────────────────────────

class TestComments:
    """Comment CRUD endpoints with pagination."""

    @pytest.mark.asyncio
    async def test_create_comment(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects", json={"name": "Comment Proj"}, headers=headers
        )
        project_id = proj_resp.json()["id"]
        task_resp = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Comment Task"},
            headers=headers,
        )
        task_id = task_resp.json()["id"]

        response = await client.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"content": "Great progress!"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Great progress!"

    @pytest.mark.asyncio
    async def test_get_comments_paginated(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects", json={"name": "Comment Paged Proj"}, headers=headers
        )
        project_id = proj_resp.json()["id"]
        task_resp = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Paged Task"},
            headers=headers,
        )
        task_id = task_resp.json()["id"]

        for i in range(3):
            await client.post(
                f"/api/v1/tasks/{task_id}/comments",
                json={"content": f"Comment {i}"},
                headers=headers,
            )

        response = await client.get(
            f"/api/v1/tasks/{task_id}/comments",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_get_comments_with_limit(self, client, test_user):
        headers = await _auth_headers(client, "test@example.com", "testpass123")
        proj_resp = await client.post(
            "/api/v1/projects", json={"name": "Lim Comment Proj"}, headers=headers
        )
        project_id = proj_resp.json()["id"]
        task_resp = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Lim Comment Task"},
            headers=headers,
        )
        task_id = task_resp.json()["id"]

        for i in range(4):
            await client.post(
                f"/api/v1/tasks/{task_id}/comments",
                json={"content": f"Comment {i}"},
                headers=headers,
            )

        response = await client.get(
            f"/api/v1/tasks/{task_id}/comments?skip=0&limit=2",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 4
