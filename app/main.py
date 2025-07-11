import secure
from fastapi import FastAPI, Request
from loguru import logger

from app.core.logger_config import log_requests, setup_logger
from app.routes import auth, task

setup_logger()

app = FastAPI()

# Add request logging middleware
app.middleware("http")(log_requests)

# Initialize secure headers
secure_headers = secure.Secure()


@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    await secure_headers.set_headers_async(response)
    return response


# Include routers

app.include_router(auth.router)
app.include_router(task.router)
