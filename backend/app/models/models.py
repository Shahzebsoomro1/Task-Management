import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Date, Index
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


# Use String(36) for UUID to be compatible with both PostgreSQL and SQLite
class UUIDType(String):
    """UUID stored as string for SQLite compatibility."""
    def __init__(self):
        super().__init__(36)


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="created_by_user", foreign_keys="Project.created_by")
    tasks = relationship("Task", back_populates="created_by_user", foreign_keys="Task.created_by")
    assigned_tasks = relationship("Task", back_populates="assigned_to_user", foreign_keys="Task.assigned_to")
    comments = relationship("Comment", back_populates="created_by_user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="projects", foreign_keys=[created_by])
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    due_date = Column(Date, nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_to_user = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    created_by_user = relationship("User", back_populates="tasks", foreign_keys=[created_by])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content = Column(String(2000), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="comments")
    created_by_user = relationship("User", back_populates="comments")
