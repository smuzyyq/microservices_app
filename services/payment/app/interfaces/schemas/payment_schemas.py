from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: UUID
    amount: float = Field(gt=0)
    currency: str = Field(default="KZT", min_length=3, max_length=8)
    method: PaymentMethod = PaymentMethod.card


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    user_id: UUID
    amount: float
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    provider_reference: str
    created_at: datetime
    updated_at: datetime
