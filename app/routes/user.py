from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/user",
    tags=["user"],
)