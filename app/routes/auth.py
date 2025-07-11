from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger_config import logger
from app.core.responses import error_response, success_response
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.users import User
from app.schemas.auth import LoginSchema, RegisterSchema, TokenSchema, UserOut

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    payload: RegisterSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email and password.

    - Validates uniqueness of email
    - Hashes password before storing
    - Logs the operation
    - Returns a standardized success or error response
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    try:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            return error_response(
                message="Email already registered",
                errors=[{"field": "email", "code": "EMAIL_ALREADY_EXISTS"}],
                status_code=400,
                request_id=request_id
            )

        # Create and persist new user
        user = User(
            user_id=uuid4(),
            email=payload.email,
            password=hash_password(payload.password)
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        log.info("User registered successfully", user_id=str(user.user_id))

        return success_response(
            data=UserOut.from_orm(user),
            message="User registered successfully",
            status_code=201,
            request_id=request_id
        )

    except Exception as e:
        log.exception("Unhandled error during registration")
        return error_response(
            message="Failed to register user",
            errors=[{"type": "exception", "detail": str(e)}],
            status_code=500,
            request_id=request_id
        )


@router.post("/login", response_model=TokenSchema)
async def login_user(
    request: Request,
    payload: LoginSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return a JWT access token.

    - Verifies user credentials
    - Issues JWT with user ID embedded
    - Logs login success or failure
    - Uses central response structure and logging
    """
    request_id = str(uuid4())
    log = logger.bind(request_id=request_id)

    try:
        # Fetch user by email
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.password):
            log.warning("Login failed: invalid credentials", email=payload.email)
            return error_response(
                message="Invalid email or password",
                errors=[{"field": "credentials", "code": "INVALID"}],
                status_code=401,
                request_id=request_id
            )

        token = create_access_token(subject=str(user.user_id))

        log.info("Login successful", user_id=str(user.user_id))

        return success_response(
            data=TokenSchema(access_token=token),
            message="Login successful",
            request_id=request_id,
            status_code=200
        )

    except Exception as e:
        log.exception("Unhandled error during login")
        return error_response(
            message="Failed to authenticate user",
            errors=[{"type": "exception", "detail": str(e)}],
            status_code=500,
            request_id=request_id
        )
