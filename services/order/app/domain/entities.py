from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    delivering = "delivering"
    delivered = "delivered"
    cancelled = "cancelled"


@dataclass
class OrderItem:
    id: UUID
    order_id: UUID
    dish_id: UUID
    dish_name: str
    quantity: int
    price: float


@dataclass
class Order:
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    status: OrderStatus
    total_price: float
    delivery_address: str
    items: list[OrderItem]
    created_at: datetime
    updated_at: datetime
