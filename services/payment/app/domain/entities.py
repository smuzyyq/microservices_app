from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"


class PaymentMethod(str, Enum):
    card = "card"


@dataclass
class Payment:
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
