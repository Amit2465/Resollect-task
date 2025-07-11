from fastapi import FastAPI
from loguru import logger

from app.core.logger_config import log_requests, setup_logger

setup_logger()

app = FastAPI()
app.middleware("http")(log_requests)