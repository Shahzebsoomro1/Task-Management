from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.core.config import get_db
from app.core.security import get_current_user, TokenData
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithTasks
from app.services.project_service import ProjectService
from app.models.models import User, UserRole

router = APIRouter(prefix="/projects", tags=["projects"])


async def get_current_user_model(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user model with role."""
    from app.services.user_service import UserService
    service = UserService(db)
    user = await service.get_user(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_create: ProjectCreate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    service = ProjectService(db)
    return await service.create_project(project_create, current_user.id)


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get all projects for current user."""
    service = ProjectService(db)
    return await service.get_user_projects(current_user.id)


@router.get("/{project_id}", response_model=ProjectWithTasks)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project."""
    service = ProjectService(db)
    project = await service.get_project(project_id, current_user.id, current_user.role)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return ProjectWithTasks.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Update a project."""
    service = ProjectService(db)
    return await service.update_project(
        project_id, project_update, current_user.id, current_user.role
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project."""
    service = ProjectService(db)
    success = await service.delete_project(project_id, current_user.id, current_user.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
