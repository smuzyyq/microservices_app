from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities import OrderStatus


class OrderItemCreate(BaseModel):
    dish_id: UUID
    dish_name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1)
    price: float = Field(gt=0)


class OrderCreate(BaseModel):
    restaurant_id: UUID
    delivery_address: str = Field(min_length=5, max_length=255)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    dish_id: UUID
    dish_name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    status: OrderStatus
    total_price: float
    delivery_address: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
