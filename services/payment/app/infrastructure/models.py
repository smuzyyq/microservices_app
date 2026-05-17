from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import PaymentMethod, PaymentStatus
from infrastructure.database import Base


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    order_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="KZT")
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, name="payment_method"), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, name="payment_status"), nullable=False)
    provider_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
