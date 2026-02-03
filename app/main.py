"""FastAPI application entrypoint for the todo backend.

This service provides a REST API for CRUD operations on todo tasks.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import engine, get_db
from app.models import Base, Task
from app.schemas import TaskCreate, TaskOut, TaskUpdate

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics."},
    {"name": "Tasks", "description": "CRUD operations for todo tasks."},
    {
        "name": "Docs",
        "description": "Helpful documentation endpoints (including WebSocket usage notes).",
    },
]

app = FastAPI(
    title="Simple Todo List API",
    description="Backend API for a simple todo list (CRUD + mark complete).",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Allow local dev frontends to call the API; adjust as needed for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (sufficient for a simple template project).
Base.metadata.create_all(bind=engine)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns a simple health status response.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health() -> dict:
    """Health check endpoint.

    Returns:
        dict: A small JSON payload indicating the service is up.
    """
    return {"status": "ok"}


@app.get(
    "/docs/ws",
    tags=["Docs"],
    summary="WebSocket usage information",
    description=(
        "This project does not expose any WebSocket endpoints. "
        "This endpoint exists to explicitly document real-time connection usage if added later."
    ),
    operation_id="websocket_usage_info",
)
# PUBLIC_INTERFACE
def websocket_usage_info() -> dict:
    """Return WebSocket usage notes.

    Returns:
        dict: Information indicating that WebSockets are not used in this API.
    """
    return {
        "websockets": "not_supported",
        "note": "No WebSocket endpoints are implemented for this service.",
    }


@app.get(
    "/tasks",
    response_model=List[TaskOut],
    tags=["Tasks"],
    summary="List tasks",
    description="Returns all tasks, ordered by newest first.",
    operation_id="list_tasks",
)
# PUBLIC_INTERFACE
def list_tasks(db: Session = Depends(get_db)) -> List[TaskOut]:
    """List all tasks.

    Args:
        db: Database session dependency.

    Returns:
        List[TaskOut]: All tasks, newest first.
    """
    tasks = db.execute(select(Task).order_by(Task.created_at.desc())).scalars().all()
    return tasks


@app.post(
    "/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    summary="Create task",
    description="Creates a new task.",
    operation_id="create_task",
)
# PUBLIC_INTERFACE
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskOut:
    """Create a new task.

    Args:
        payload: Task creation payload.
        db: Database session dependency.

    Returns:
        TaskOut: Newly created task.
    """
    task = Task(title=payload.title, description=payload.description, completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    tags=["Tasks"],
    summary="Get task",
    description="Fetch a single task by id.",
    operation_id="get_task",
)
# PUBLIC_INTERFACE
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskOut:
    """Get a task by id.

    Args:
        task_id: Task identifier.
        db: Database session dependency.

    Raises:
        HTTPException: If the task does not exist.

    Returns:
        TaskOut: The requested task.
    """
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskOut,
    tags=["Tasks"],
    summary="Update task",
    description="Partially update a task (title/description/completed).",
    operation_id="update_task",
)
# PUBLIC_INTERFACE
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskOut:
    """Update an existing task.

    Args:
        task_id: Task identifier.
        payload: Partial update payload.
        db: Database session dependency.

    Raises:
        HTTPException: If the task does not exist.

    Returns:
        TaskOut: Updated task.
    """
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    summary="Delete task",
    description="Deletes a task by id.",
    operation_id="delete_task",
)
# PUBLIC_INTERFACE
def delete_task(task_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a task.

    Args:
        task_id: Task identifier.
        db: Database session dependency.

    Raises:
        HTTPException: If the task does not exist.

    Returns:
        Response: Empty 204 response.
    """
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
