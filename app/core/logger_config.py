import os
import sys
import time
import uuid
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import Response
from loguru import logger

# Get the current application environment
APP_ENV = os.getenv("APP_ENV", "development").lower()

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Set a default logger context
logger = logger.bind(request_id="unknown")


def setup_logger():
    """
    Configure the global logger based on the application environment.

    - In production: serialize logs and disable debugging details.
    - In development: enable detailed, colorized logs for easier debugging.
    """
    logger.remove()

    if APP_ENV == "production":
        logger.add(
            sys.stdout,
            level="INFO",
            serialize=True,
            backtrace=False,
            diagnose=False,
            format="{time} {level} {message}",
        )
        logger.add(
            "logs/prod.log",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            level="INFO",
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            colorize=True,
            backtrace=True,
            diagnose=True,
            level="DEBUG",
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan><b>{file}</b></cyan>:"
                "<yellow><b>{function}</b></yellow>:"
                "<magenta><b>{line}</b></magenta> - "
                "<level>{message}</level>"
            ),
        )
        logger.add(
            "logs/dev.log",
            rotation="100 MB",
            retention="7 days",
            compression="zip",
            level="DEBUG",
            backtrace=True,
            diagnose=True,
        )


async def log_requests(request: Request, call_next):
    """
    Middleware to log incoming HTTP requests and responses with duration and status.

    Generates a unique request ID and logs:
    - HTTP method and path
    - Response status and reason
    - Duration of the request
    - Client IP

    Adds an 'X-Request-ID' header to the response.
    """
    request_id = str(uuid.uuid4())
    logger_ctx = logger.bind(request_id=request_id)
    start_time = time.time()

    try:
        response: Response = await call_next(request)
    except Exception:
        logger_ctx.exception("Unhandled exception")
        raise

    duration_ms = round((time.time() - start_time) * 1000, 2)
    status = response.status_code
    reason_phrase = (
        HTTPStatus(status).phrase if status in HTTPStatus._value2member_map_ else ""
    )
    status_info = f"{status} {reason_phrase}".strip()
    log_fn = logger_ctx.error if status >= 400 else logger_ctx.info

    log_fn(
        f"{request.method} {request.url.path} → {status_info} [{duration_ms}ms]",
        method=request.method,
        path=request.url.path,
        status=status,
        reason=reason_phrase,
        duration_ms=duration_ms,
        client=request.client.host,
    )

    response.headers["X-Request-ID"] = request_id
    return response