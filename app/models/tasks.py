from uuid import uuid4

from db.base import Base
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Task(Base):
    """
    ORM model representing a Task.
    Tasks are linked to users and include deadlines, completion state, and status flags.
    """
    __tablename__ = "tasks"

    task_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        unique=True,
        index=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title = Column(
        Text,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    deadline = Column(
        DateTime(timezone=True),
        nullable=False
    )

    completed = Column(
        Boolean,
        nullable=False,
        default=False
    )

    status = Column(
        String(10),
        nullable=False,
        default="upcoming"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship(
        "User",
        back_populates="tasks"
    )

    # Add check constraint to enforce allowed status values
    __table_args__ = (
        CheckConstraint(
            "status IN ('upcoming', 'completed', 'missed')",
            name="status_valid_values"
        ),
    )   
