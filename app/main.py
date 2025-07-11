from fastapi import FastAPI
from loguru import logger

from app.core.logger_config import log_requests, setup_logger

from .routes import auth, task, user

setup_logger()

app = FastAPI()
app.middleware("http")(log_requests)
app.include_router(task.router)
app.include_router(user.router)
app.include_router(auth.router)