from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.project_repository import ProjectRepository
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.models.models import Project, UserRole
from fastapi import HTTPException, status
from typing import Optional, List


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: AsyncSession):
        self.repository = ProjectRepository(db)

    async def create_project(
        self, project_create: ProjectCreate, user_id: str
    ) -> ProjectResponse:
        """Create a new project."""
        project = Project(
            name=project_create.name,
            description=project_create.description,
            created_by=str(user_id),
        )
        self.repository.db.add(project)
        await self.repository.db.commit()
        await self.repository.db.refresh(project)
        return ProjectResponse.model_validate(project)

    async def get_project(self, project_id: str, user_id: str, user_role: UserRole) -> Optional[Project]:
        """Get a project by ID (with tasks eagerly loaded)."""
        project = await self.repository.get_with_tasks(project_id)
        if not project:
            return None

        # Check authorization (admin can view all, user can only view their own)
        if user_role != UserRole.admin and project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this project",
            )
        return project

    async def get_user_projects(
        self, user_id: str, skip: int = 0, limit: int = 100, user_role: UserRole = UserRole.user
    ):
        """Get paginated projects. Admins see all; regular users see only their own."""
        is_admin = user_role == UserRole.admin
        return await self.repository.get_user_projects(user_id, skip=skip, limit=limit, is_admin=is_admin)

    async def update_project(
        self, project_id: str, project_update: ProjectUpdate, user_id: str, user_role: UserRole
    ) -> ProjectResponse:
        """Update a project."""
        project = await self.get_project(project_id, user_id, user_role)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Check authorization
        if user_role != UserRole.admin and project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this project",
            )

        project = await self.repository.update(project, project_update)
        return ProjectResponse.model_validate(project)

    async def delete_project(self, project_id: str, user_id: str, user_role: UserRole) -> bool:
        """Delete a project."""
        project = await self.get_project(project_id, user_id, user_role)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Check authorization
        if user_role != UserRole.admin and project.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project",
            )

        return await self.repository.delete_by_id(project_id)
