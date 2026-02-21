from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class TaskStatusEnum(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.user


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRoleEnum] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(ProjectBase):
    id: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectWithTasks(ProjectResponse):
    tasks: List["TaskResponse"] = []


# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatusEnum = TaskStatusEnum.todo
    priority: TaskPriorityEnum = TaskPriorityEnum.medium
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: TaskPriorityEnum = TaskPriorityEnum.medium
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None


class TaskResponse(TaskBase):
    id: str
    project_id: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskWithComments(TaskResponse):
    comments: List["CommentResponse"] = []


# Comment Schemas
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(CommentBase):
    id: str
    task_id: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Pagination
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# Filter and Sort
class TaskFilterParams(BaseModel):
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    project_id: Optional[str] = None
    assigned_to: Optional[str] = None
    order_by: Optional[str] = Field(None, pattern="^(due_date|priority|created_at)$")
    order_desc: bool = False
