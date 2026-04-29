from uuid import UUID

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    phone: str | None
    avatar_url: str | None
    default_address: str | None


class ProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=30)
    avatar_url: str | None = Field(default=None, max_length=500)
    default_address: str | None = Field(default=None, max_length=255)


class AddressCreate(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    full_address: str = Field(min_length=5, max_length=255)
    is_default: bool = False


class AddressResponse(BaseModel):
    id: UUID
    user_id: UUID
    label: str
    full_address: str
    is_default: bool
