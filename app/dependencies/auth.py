from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.users import User

security = HTTPBearer()  # Enables Swagger lock icon


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current user from JWT Authorization header.

    Decodes the JWT, logs each step, and returns the authenticated user.

    Raises:
        HTTPException (401 or 404) on failure.

    Returns:
        User: authenticated user instance
    """
    request_id = str(uuid4())
    bound_logger = logger.bind(request_id=request_id)

    token = credentials.credentials  # Extracts token from "Bearer <token>"

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            bound_logger.warning("JWT missing subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no subject",
            )

        user = await db.get(User, UUID(user_id))
        if not user:
            bound_logger.warning("User not found", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        bound_logger.info("Authenticated user successfully", user_id=str(user.user_id))
        return user

    except JWTError as e:
        bound_logger.warning("JWT decode failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    except Exception as e:
        bound_logger.exception("Unhandled error in get_current_user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )
