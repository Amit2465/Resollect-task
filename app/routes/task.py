from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.core.responses import error_response, success_response
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.tasks import Task
from app.models.users import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])


def calculate_status(task: Task) -> None:
    """
    Automatically update the task status based on deadline and completion state.
    """
    now = datetime.now(tz=timezone.utc)
    if task.completed:
        task.status = "completed"
    elif task.deadline < now:
        task.status = "missed"
    else:
        task.status = "upcoming"


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task for the current user.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    try:
        task = Task(
            task_id=uuid4(),
            user_id=current_user.user_id,
            title=payload.title,
            description=payload.description,
            deadline=payload.deadline,
            completed=False,
        )
        calculate_status(task)
        db.add(task)
        await db.commit()
        await db.refresh(task)

        log.info("Task created", task_id=str(task.task_id))
        task_out = TaskOut.model_validate(task)
        return success_response(
            data=task_out,
            message="Task created successfully",
            request_id=request_id,
            status_code=201,
        )

    except Exception as e:
        log.exception("Failed to create task")
        return error_response(
            message="Failed to create task",
            status_code=500,
            errors=[{"type": "exception", "detail": str(e)}],
            request_id=request_id,
        )


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all tasks for the current user.
    Status is recalculated before returning.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    try:
        result = await db.execute(
            select(Task).where(Task.user_id == current_user.user_id)
        )
        tasks = result.scalars().all()

        for task in tasks:
            calculate_status(task)

        tasks_out = [TaskOut.model_validate(task) for task in tasks]
        return success_response(
            data=tasks_out,
            message="Tasks retrieved successfully",
            request_id=request_id,
        )

    except Exception as e:
        log.exception("Failed to fetch tasks")
        return error_response(
            message="Error retrieving tasks",
            status_code=500,
            errors=[{"type": "exception", "detail": str(e)}],
            request_id=request_id,
        )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single task by ID for the current user.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    task = await db.get(Task, task_id)
    if not task or task.user_id != current_user.user_id:
        log.warning("Unauthorized or not found", task_id=str(task_id))
        return error_response(
            message="Task not found", status_code=404, request_id=request_id
        )

    calculate_status(task)
    task_out = TaskOut.model_validate(task)
    return success_response(
        data=task_out, message="Task retrieved successfully", request_id=request_id
    )


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a task's details and status.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    task = await db.get(Task, task_id)
    if not task or task.user_id != current_user.user_id:
        log.warning("Unauthorized update attempt", task_id=str(task_id))
        return error_response(
            message="Task not found", status_code=404, request_id=request_id
        )

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    calculate_status(task)
    await db.commit()
    await db.refresh(task)
    task_out = TaskOut.model_validate(task)
    return success_response(
        data=task_out, message="Task updated successfully", request_id=request_id
    )


@router.patch("/{task_id}/complete", response_model=TaskOut)
async def mark_complete(
    task_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as completed.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    task = await db.get(Task, task_id)
    if not task or task.user_id != current_user.user_id:
        log.warning("Unauthorized complete attempt", task_id=str(task_id))
        return error_response(
            message="Task not found", status_code=404, request_id=request_id
        )

    task.completed = True
    calculate_status(task)
    await db.commit()
    await db.refresh(task)
    task_out = TaskOut.model_validate(task)
    return success_response(
        data=task_out, message="Task marked as completed", request_id=request_id
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a task owned by the current user.
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    task = await db.get(Task, task_id)
    if not task or task.user_id != current_user.user_id:
        log.warning("Unauthorized delete attempt", task_id=str(task_id))
        return error_response(
            message="Task not found", status_code=404, request_id=request_id
        )

    await db.delete(task)
    await db.commit()
    return success_response(
        message="Task deleted successfully", status_code=204, request_id=request_id
    )
