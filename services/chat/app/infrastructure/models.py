from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities import SenderRole
from infrastructure.database import Base


class ChatRoomModel(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    order_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    courier_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    room_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), ForeignKey("chat_rooms.id"), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    sender_role: Mapped[SenderRole] = mapped_column(Enum(SenderRole, name="sender_role"), nullable=False)
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
