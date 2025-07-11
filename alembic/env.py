"""
Alembic migration environment.

This configuration file integrates Alembic with an async SQLAlchemy engine
using the asyncpg driver for PostgreSQL. It dynamically loads the database
URL from a .env file and uses SQLAlchemy metadata from the application's models.
"""

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alembic Config object, provides access to the .ini file values
config = context.config

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the metadata from the application models
# Adjust this import to reflect your actual project structure
from app.db.base import Base

# Assign the metadata object for 'autogenerate' support
target_metadata = Base.metadata

# Construct async database URL from environment variables
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

ASYNC_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def run_migrations_offline() -> None:
    """
    Run Alembic migrations in 'offline' mode.

    In this mode, Alembic emits SQL statements to the script output
    without executing them against a live database.
    """
    context.configure(
        url=ASYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Apply migrations using a given connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run Alembic migrations in 'online' mode with an async engine.

    Establishes a real connection to the database using asyncpg and applies
    the migrations using the provided metadata.
    """
    connectable = create_async_engine(ASYNC_DB_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Determine whether to run migrations in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

