from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    customer = "customer"
    courier = "courier"
    admin = "admin"


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


@dataclass
class TokenPayload:
    user_id: UUID
    email: str
    role: str
