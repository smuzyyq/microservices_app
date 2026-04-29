from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities import SenderRole


class RoomCreate(BaseModel):
    order_id: UUID
    customer_id: UUID


class RoomResponse(BaseModel):
    id: UUID
    order_id: UUID
    customer_id: UUID
    courier_id: UUID | None
    is_active: bool
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID
    sender_role: SenderRole
    content: str
    is_read: bool
    created_at: datetime
