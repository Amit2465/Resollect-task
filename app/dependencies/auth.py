from uuid import UUID, uuid4

from core.security import decode_access_token
from db.models.user import User
from dependencies.db import get_db
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from secure import SecureHeaders
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_info import logger

secure_headers = SecureHeaders()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from JWT Authorization header.

    Extracts the token securely using `SecureHeaders`,
    decodes the token, logs the process,
    and returns the user from the DB.

    Raises:
        HTTPException (401 or 404) on failure.

    Returns:
        User: authenticated user instance
    """
    request_id = str(uuid4())
    bound_logger = logger.bind(request_id=request_id)

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        bound_logger.warning("Missing or malformed Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            bound_logger.warning("JWT missing subject")
            raise HTTPException(status_code=401, detail="Invalid token: no subject")

        user = await db.get(User, UUID(user_id))
        if not user:
            bound_logger.warning("User not found", user_id=user_id)
            raise HTTPException(status_code=404, detail="User not found")

        bound_logger.info("Authenticated user successfully", user_id=str(user.user_id))
        return user

    except JWTError as e:
        bound_logger.warning("JWT decode failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    except Exception as e:
        bound_logger.exception("Unhandled error in get_current_user")
        raise HTTPException(status_code=500, detail="Authentication error")
