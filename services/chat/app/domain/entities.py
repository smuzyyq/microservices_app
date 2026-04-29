from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class SenderRole(str, Enum):
    customer = "customer"
    courier = "courier"
    support = "support"


@dataclass
class ChatRoom:
    id: UUID
    order_id: UUID
    customer_id: UUID
    courier_id: UUID | None
    is_active: bool
    created_at: datetime


@dataclass
class Message:
    id: UUID
    room_id: UUID
    sender_id: UUID
    sender_role: SenderRole
    content: str
    is_read: bool
    created_at: datetime
