from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# JWT config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a signed JWT access token.

    Args:
        subject: user ID or any unique identifier to embed as 'sub'
        expires_delta: optional expiration delta

    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token and return its payload.
    Raises JWTError if decoding fails or token is invalid/expired.

    Args:
        token: the encoded JWT string

    Returns:
        dict: decoded token payload
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
