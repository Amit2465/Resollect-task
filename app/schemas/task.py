from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """
    Shared properties for creating and updating tasks.
    """

    title: str = Field(
        ..., min_length=1, max_length=255, description="Title of the task"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Optional task description"
    )
    deadline: datetime = Field(..., description="Task deadline")


class TaskCreate(TaskBase):
    """
    Schema for task creation request.
    """

    title: str
    description: Optional[str] = None
    deadline: datetime


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    Supports partial updates.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    deadline: Optional[datetime] = None
    completed: Optional[bool] = None


class TaskOut(BaseModel):
    """
    Schema for task response returned to clients.
    """

    task_id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    deadline: datetime
    completed: bool
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
