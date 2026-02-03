"""Pydantic models (schemas) for API I/O."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Shared fields for task I/O."""

    title: str = Field(..., min_length=1, max_length=200, description="Short title of the task.")
    description: Optional[str] = Field(
        default=None, max_length=2000, description="Optional longer description of the task."
    )


class TaskCreate(TaskBase):
    """Payload to create a task."""


class TaskUpdate(BaseModel):
    """Payload to update a task. All fields are optional."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Updated title.")
    description: Optional[str] = Field(default=None, max_length=2000, description="Updated description.")
    completed: Optional[bool] = Field(default=None, description="Set task completion state.")


class TaskOut(TaskBase):
    """Task returned from the API."""

    id: int = Field(..., description="Unique identifier of the task.")
    completed: bool = Field(..., description="Whether the task is completed.")
    created_at: datetime = Field(..., description="UTC timestamp when the task was created.")
    updated_at: datetime = Field(..., description="UTC timestamp when the task was last updated.")

    class Config:
        from_attributes = True
