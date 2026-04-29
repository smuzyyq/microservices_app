from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserProfile:
    id: UUID
    user_id: UUID
    phone: str | None
    avatar_url: str | None
    default_address: str | None


@dataclass
class DeliveryAddress:
    id: UUID
    user_id: UUID
    label: str
    full_address: str
    is_default: bool
