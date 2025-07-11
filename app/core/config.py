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

      # Secret key for cryptographic operations
    SECRET_KEY: str

    # Redis settings for rate limiter
    REDIS_URL: str = "redis://redis:6379"

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

# Hardcoded PostgreSQL connection URL (edit as needed)
ASYNC_DATABASE_URL = "postgresql+asyncpg://Amit:Test@db:5432/TaskEngineDB"

print(ASYNC_DATABASE_URL)  

"""
SQLAlchemy async-compatible database connection URL string.

Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
Used by SQLAlchemy `create_async_engine`.
"""
