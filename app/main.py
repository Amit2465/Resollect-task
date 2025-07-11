import secure
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.limiter import limiter
from app.core.logger_config import log_requests, setup_logger
from app.routes import auth, task

setup_logger()
app = FastAPI()

# Add request logging
app.middleware("http")(log_requests)

# Initialize global rate limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# Register custom handler for rate limit violations
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Too many requests, please try again later.",
            "limit": exc.detail,
            "path": request.url.path,
        },
        headers=getattr(exc, "headers", {}),
    )


# Secure headers middleware
secure_headers = secure.Secure()


@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    await secure_headers.set_headers_async(response)
    return response


# Include route modules
app.include_router(auth.router)
app.include_router(task.router)
