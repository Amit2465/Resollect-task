from redis import asyncio as aioredis
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Initialize Redis client
redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

# Create a global rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    in_memory_fallback_enabled=True,
    application_limits=["200/minute"],
)
