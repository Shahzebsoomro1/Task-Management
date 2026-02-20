from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskStatusEnum
from app.models.models import Task, UserRole, TaskStatus
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional, List, Tuple


class TaskService:
    """Service for task operations."""

    def __init__(self, db: AsyncSession):
        self.repository = TaskRepository(db)

    async def create_task(
        self, task_create: TaskCreate, project_id: UUID, user_id: UUID
    ) -> TaskResponse:
        """Create a new task."""
        # Create task with initial status as todo
        task_dict = task_create.model_dump()
        task_dict["project_id"] = project_id
        task_dict["created_by"] = user_id
        task_dict["status"] = TaskStatus.todo

        # Create a new TaskCreate-like object for the repository
        from app.schemas.schemas import TaskCreate as TaskCreateSchema
        task_create_with_ids = TaskCreateSchema(**task_dict)

        task = await self.repository.create(task_create_with_ids)
        task.project_id = project_id
        task.created_by = user_id
        await self.repository.db.commit()
        await self.repository.db.refresh(task)
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: UUID, user_id: UUID, user_role: UserRole) -> Optional[Task]:
        """Get a task by ID."""
        task = await self.repository.get(task_id)
        if not task:
            return None

        # Check authorization
        if user_role != UserRole.admin:
            if task.created_by != user_id and task.assigned_to != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this task",
                )
        return task

    async def get_project_tasks(
        self,
        project_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        status: Optional[TaskStatusEnum] = None,
        assigned_to: Optional[UUID] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a project."""
        # For non-admin users, only return their tasks
        if user_role != UserRole.admin:
            assigned_to = user_id

        task_status = None
        if status:
            task_status = TaskStatus[status.value]

        tasks, count = await self.repository.get_project_tasks(
            project_id=project_id,
            status=task_status,
            assigned_to=assigned_to,
            order_by=order_by,
            order_desc=order_desc,
            skip=skip,
            limit=limit,
        )
        return tasks, count

    async def update_task(
        self, task_id: UUID, task_update: TaskUpdate, user_id: UUID, user_role: UserRole
    ) -> TaskResponse:
        """Update a task."""
        task = await self.get_task(task_id, user_id, user_role)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Check authorization
        if user_role != UserRole.admin and task.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task",
            )

        task = await self.repository.update(task, task_update)
        return TaskResponse.model_validate(task)

    async def delete_task(self, task_id: UUID, user_id: UUID, user_role: UserRole) -> bool:
        """Delete a task."""
        task = await self.get_task(task_id, user_id, user_role)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Check authorization
        if user_role != UserRole.admin and task.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task",
            )

        return await self.repository.delete_by_id(task_id)
