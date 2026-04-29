from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from domain.entities import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str
    role: str
    access_token: str


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class TokenVerifyResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    role: str
    valid: bool
