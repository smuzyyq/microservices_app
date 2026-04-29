from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    default_address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    addresses = relationship("DeliveryAddressModel", back_populates="profile", cascade="all, delete-orphan")


class DeliveryAddressModel(Base):
    __tablename__ = "delivery_addresses"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    full_address: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile = relationship("UserProfileModel", back_populates="addresses")
