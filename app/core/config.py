"""
Application configuration module.

This module provides a centralized settings object that loads and caches environment variables
using Pydantic's BaseSettings, leveraging a .env file for configuration.

It exposes:
- `settings`: a lazily loaded singleton containing all config values.
- `ASYNC_DATABASE_URL`: fully composed SQLAlchemy-compatible async PostgreSQL connection URL.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    These settings are used throughout the app, including for database connection,
    and are loaded from a `.env` file by default.

    Attributes:
        POSTGRES_DB (str): Name of the PostgreSQL database.
        POSTGRES_USER (str): PostgreSQL username.
        POSTGRES_PASSWORD (str): PostgreSQL password.
        POSTGRES_HOST (str): Hostname of the PostgreSQL service (e.g. "localhost" or "db" in Docker).
        POSTGRES_PORT (int): Port number for PostgreSQL (default: 5432).
    """
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    SECRET_KEY: str

    class Config:
        # Auto-load this file for environment variables
        env_file = ".env"  


@lru_cache()
def get_settings() -> Settings:
    """
    Lazily loads and caches the settings object.

    Returns:
        Settings: The loaded application settings.
    """
    return Settings()


# Load the singleton settings object
settings = get_settings()

# Construct the async database URL used by SQLAlchemy
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
"""
SQLAlchemy async-compatible database connection URL string.

Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
Used by SQLAlchemy `create_async_engine`.
"""
