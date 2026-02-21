from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.config import get_db
from app.core.security import get_current_user, TokenData
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskWithComments, TaskStatusEnum
from app.services.task_service import TaskService
from app.models.models import User

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


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


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: str,
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    service = TaskService(db)
    return await service.create_task(task_create, project_id, current_user.id)


@router.get("", response_model=dict)
async def get_tasks(
    project_id: str,
    status: Optional[TaskStatusEnum] = Query(None),
    assigned_to: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    order_desc: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get tasks for a project with filtering and pagination."""
    service = TaskService(db)
    tasks, total = await service.get_project_tasks(
        project_id=project_id,
        user_id=current_user.id,
        user_role=current_user.role,
        status=status,
        assigned_to=assigned_to,
        order_by=order_by,
        order_desc=order_desc,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [TaskResponse.model_validate(task) for task in tasks],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{task_id}", response_model=TaskWithComments)
async def get_task(
    project_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific task with comments."""
    service = TaskService(db)
    task = await service.get_task(task_id, current_user.id, current_user.role)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return TaskWithComments.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Update a task."""
    service = TaskService(db)
    return await service.update_task(task_id, task_update, current_user.id, current_user.role)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    service = TaskService(db)
    success = await service.delete_task(task_id, current_user.id, current_user.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
