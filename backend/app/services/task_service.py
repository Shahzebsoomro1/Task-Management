from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskStatusEnum
from app.models.models import Task, UserRole, TaskStatus
from fastapi import HTTPException, status
from typing import Optional, List, Tuple


class TaskService:
    """Service for task operations."""

    def __init__(self, db: AsyncSession):
        self.repository = TaskRepository(db)

    async def create_task(
        self, task_create: TaskCreate, project_id: str, user_id: str
    ) -> TaskResponse:
        """Create a new task."""
        task = Task(
            title=task_create.title,
            description=task_create.description,
            status=TaskStatus.todo,
            priority=task_create.priority,
            due_date=task_create.due_date,
            assigned_to=str(task_create.assigned_to) if task_create.assigned_to else None,
            project_id=str(project_id),
            created_by=str(user_id),
        )
        self.repository.db.add(task)
        await self.repository.db.commit()
        await self.repository.db.refresh(task)
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: str, user_id: str, user_role: UserRole) -> Optional[Task]:
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
        project_id: str,
        user_id: str,
        user_role: UserRole,
        status: Optional[TaskStatusEnum] = None,
        assigned_to: Optional[str] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a project."""
        # For non-admin users, filter to tasks they created or are assigned to
        filter_user_id = None if user_role == UserRole.admin else user_id

        task_status = None
        if status:
            task_status = TaskStatus[status.value]

        tasks, count = await self.repository.get_project_tasks(
            project_id=project_id,
            status=task_status,
            assigned_to=assigned_to,
            user_id=filter_user_id,
            order_by=order_by,
            order_desc=order_desc,
            skip=skip,
            limit=limit,
        )
        return tasks, count

    async def update_task(
        self, task_id: str, task_update: TaskUpdate, user_id: str, user_role: UserRole
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

    async def delete_task(self, task_id: str, user_id: str, user_role: UserRole) -> bool:
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
