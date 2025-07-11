import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import existing logger configuration
from app.core.logger_config import logger


class ApiResponse(BaseModel):
    """
    Standardized API response model.
    
    This model ensures all API responses follow a consistent structure
    with proper typing and validation.
    
    Attributes:
        success (bool): Indicates if the operation was successful
        message (str): Human-readable message describing the result
        data (Any, optional): Response payload data
        timestamp (datetime): When the response was generated
        request_id (str): Unique identifier for request tracing
        errors (List[Dict], optional): Error details for failed operations
    """
    
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    errors: Optional[List[Dict[str, Any]]] = Field(default=None, description="Error details for failed operations")


class ResponseBuilder:
    """
    Builder class for creating standardized API responses.
    
    This class provides static methods to build success and error responses
    with consistent formatting and automatic logging integration.
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        request_id: Optional[str] = None
    ) -> ApiResponse:
        """
        Create a successful response.
        
        Args:
            data: Response payload data
            message: Success message to display
            request_id: Optional request identifier for tracing
            
        Returns:
            ApiResponse: Standardized success response object
        """
        response = ApiResponse(
            success=True,
            message=message,
            data=data,
            request_id=request_id or str(uuid.uuid4())
        )
        
        # Log successful operation using existing logger
        logger.bind(request_id=response.request_id).info(
            f"Success response: {message}",
            response_type="success",
            has_data=data is not None
        )
        
        return response
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[List[Dict[str, Any]]] = None,
        data: Any = None,
        request_id: Optional[str] = None
    ) -> ApiResponse:
        """
        Create an error response.
        
        Args:
            message: Error message to display
            errors: List of detailed error information
            data: Optional data to include with error response
            request_id: Optional request identifier for tracing
            
        Returns:
            ApiResponse: Standardized error response object
        """
        response = ApiResponse(
            success=False,
            message=message,
            data=data,
            errors=errors,
            request_id=request_id or str(uuid.uuid4())
        )
        
        # Log error operation using existing logger
        logger.bind(request_id=response.request_id).error(
            f"Error response: {message}",
            response_type="error",
            error_count=len(errors) if errors else 0
        )
        
        return response


class ResponseHandler:
    """
    Handler for converting API responses to HTTP responses.

    This class manages the conversion of ApiResponse objects to FastAPI
    JSONResponse objects with appropriate HTTP status codes and proper encoding.
    """

    @staticmethod
    def create_response(api_response: ApiResponse, status_code: int = None) -> JSONResponse:
        """
        Convert ApiResponse to JSONResponse with appropriate status code.

        Handles serialization of non-JSON-native types such as datetime using
        FastAPI's jsonable_encoder to ensure the response is valid.

        Args:
            api_response: The standardized API response object
            status_code: Optional HTTP status code override

        Returns:
            JSONResponse: FastAPI JSON response ready for return
        """
        # Determine status code based on response success if not provided
        status_code = status_code if status_code is not None else (200 if api_response.success else 500)

        # Serialize the response using FastAPI's encoder to handle datetime and other non-serializable types
        response = JSONResponse(
            content=jsonable_encoder(api_response),
            status_code=status_code
        )

        # Add request ID to response headers for tracing/debugging purposes
        response.headers["X-Request-ID"] = api_response.request_id

        return response


def create_exception_handler():
    """
    Create a global exception handler for FastAPI applications.
    
    This handler catches all unhandled exceptions and converts them into
    standardized error responses with proper logging using the existing logger.
    
    Returns:
        Callable: Exception handler function for FastAPI
    """
    
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Global exception handler for unhandled exceptions.
        
        Args:
            request: FastAPI request object
            exc: The exception that was raised
            
        Returns:
            JSONResponse: Standardized error response
        """
        request_id = str(uuid.uuid4())
        
        # Log the exception with full context using existing logger
        logger.bind(request_id=request_id).exception(
            f"Unhandled exception in {request.method} {request.url.path}",
            exception_type=type(exc).__name__,
            path=request.url.path,
            method=request.method,
            client_host=request.client.host if request.client else "unknown"
        )
        
        # Handle HTTPException specifically
        if isinstance(exc, HTTPException):
            response = ResponseBuilder.error(
                message=str(exc.detail),
                request_id=request_id
            )
            return ResponseHandler.create_response(response, exc.status_code)
        
        # Handle all other exceptions as internal server errors
        response = ResponseBuilder.error(
            message="Internal server error occurred",
            errors=[{"type": "internal_error", "detail": "An unexpected error occurred"}],
            request_id=request_id
        )
        return ResponseHandler.create_response(response, 500)
    
    return exception_handler


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create a successful JSON response.
    
    Args:
        data: Response payload data
        message: Success message to display
        status_code: HTTP status code (default: 200)
        request_id: Optional request identifier for tracing
        
    Returns:
        JSONResponse: FastAPI JSON response with success status
        
    Example:
        >>> return success_response(
        ...     data={"users": [{"id": 1, "name": "John"}]},
        ...     message="Users retrieved successfully"
        ... )
    """
    api_response = ResponseBuilder.success(data=data, message=message, request_id=request_id)
    return ResponseHandler.create_response(api_response, status_code)


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[Dict[str, Any]]] = None,
    data: Any = None,
    status_code: int = 500,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create an error JSON response.
    
    Args:
        message: Error message to display
        errors: List of detailed error information
        data: Optional data to include with error response
        status_code: HTTP status code (default: 500)
        request_id: Optional request identifier for tracing
        
    Returns:
        JSONResponse: FastAPI JSON response with error status
        
    Example:
        >>> return error_response(
        ...     message="User not found",
        ...     status_code=404,
        ...     errors=[{"field": "user_id", "code": "NOT_FOUND"}]
        ... )
    """
    api_response = ResponseBuilder.error(
        message=message,
        errors=errors,
        data=data,
        request_id=request_id
    )
    return ResponseHandler.create_response(api_response, status_code)