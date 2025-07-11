from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterSchema(BaseModel):
    """
    Schema for user registration input.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")


class LoginSchema(BaseModel):
    """
    Schema for user login input.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenSchema(BaseModel):
    """
    Schema for JWT access token output.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Type of the token")


class UserOut(BaseModel):
    """
    Schema for returning user details in responses.
    """
    user_id: UUID = Field(..., description="Unique ID of the user")
    email: EmailStr = Field(..., description="User's email address")

    model_config = ConfigDict(from_attributes=True)
