import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.logger_config import logger


class ApiResponse(BaseModel):
    """
    Standardized API response model.
    """

    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data payload")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp",
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier",
    )
    errors: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Error details for failed operations"
    )


class ResponseBuilder:
    """
    Builder class for creating standardized API responses.
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        request_id: Optional[str] = None,
    ) -> ApiResponse:
        response = ApiResponse(
            success=True,
            message=message,
            data=data,
            request_id=request_id or str(uuid.uuid4()),
        )

        logger.bind(request_id=response.request_id).info(
            f"Success response: {message}",
            response_type="success",
            has_data=data is not None,
        )

        return response

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[List[Dict[str, Any]]] = None,
        data: Any = None,
        request_id: Optional[str] = None,
    ) -> ApiResponse:
        response = ApiResponse(
            success=False,
            message=message,
            data=data,
            errors=errors,
            request_id=request_id or str(uuid.uuid4()),
        )

        logger.bind(request_id=response.request_id).error(
            f"Error response: {message}",
            response_type="error",
            error_count=len(errors) if errors else 0,
        )

        return response


class ResponseHandler:
    """
    Handler for converting API responses to HTTP responses.
    """

    @staticmethod
    def create_response(
        api_response: ApiResponse, status_code: int = None
    ) -> JSONResponse:
        status_code = (
            status_code
            if status_code is not None
            else (200 if api_response.success else 500)
        )

        response = JSONResponse(
            content=jsonable_encoder(api_response), status_code=status_code
        )

        response.headers["X-Request-ID"] = api_response.request_id
        return response


def create_exception_handler():
    """
    Create a global exception handler for FastAPI applications.
    """

    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = str(uuid.uuid4())

        logger.bind(request_id=request_id).exception(
            f"Unhandled exception in {request.method} {request.url.path}",
            exception_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            client_host=request.client.host if request.client else "unknown",
        )

        if isinstance(exc, HTTPException):
            response = ResponseBuilder.error(
                message=str(exc.detail), request_id=request_id
            )
            return ResponseHandler.create_response(response, exc.status_code)

        response = ResponseBuilder.error(
            message="Internal server error occurred",
            errors=[
                {"type": "internal_error", "detail": "An unexpected error occurred"}
            ],
            request_id=request_id,
        )
        return ResponseHandler.create_response(response, 500)

    return exception_handler


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """
    Create a successful JSON response.
    """
    # Convert single ORM object
    if (
        hasattr(data, "__class__")
        and hasattr(data.__class__, "model_config")
        and getattr(data.__class__.model_config, "from_attributes", False)
    ):
        data = data.__class__.from_orm(data)

    # Convert list of ORM objects
    elif (
        isinstance(data, list)
        and data
        and hasattr(data[0].__class__, "model_config")
        and getattr(data[0].__class__.model_config, "from_attributes", False)
    ):
        model_cls = data[0].__class__
        data = [model_cls.from_orm(item) for item in data]

    api_response = ResponseBuilder.success(
        data=data, message=message, request_id=request_id
    )
    return ResponseHandler.create_response(api_response, status_code)


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[Dict[str, Any]]] = None,
    data: Any = None,
    status_code: int = 500,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """
    Create an error JSON response.
    """
    api_response = ResponseBuilder.error(
        message=message, errors=errors, data=data, request_id=request_id
    )
    return ResponseHandler.create_response(api_response, status_code)
