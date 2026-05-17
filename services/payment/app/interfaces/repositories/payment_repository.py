from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import Payment, PaymentMethod, PaymentStatus
from domain.exceptions import DatabaseConnectionError
from infrastructure.models import PaymentModel


class IPaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> Payment:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, payment_id: UUID) -> Payment | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_order_id(self, order_id: UUID) -> Payment | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[Payment]:
        raise NotImplementedError


class PaymentRepository(IPaymentRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, payment: Payment) -> Payment:
        try:
            model = PaymentModel(
                id=payment.id,
                order_id=payment.order_id,
                user_id=payment.user_id,
                amount=payment.amount,
                currency=payment.currency,
                method=payment.method,
                status=payment.status,
                provider_reference=payment.provider_reference,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
            )
            self.session.add(model)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            raise DatabaseConnectionError(f"Failed to save payment: {exc}") from exc
        return self.find_by_id(payment.id)  # type: ignore[return-value]

    def find_by_id(self, payment_id: UUID) -> Payment | None:
        try:
            model = self.session.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch payment by id: {exc}") from exc
        return self._to_entity(model) if model else None

    def find_by_order_id(self, order_id: UUID) -> Payment | None:
        try:
            model = self.session.query(PaymentModel).filter(PaymentModel.order_id == order_id).first()
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch payment by order id: {exc}") from exc
        return self._to_entity(model) if model else None

    def find_by_user(self, user_id: UUID) -> list[Payment]:
        try:
            models = (
                self.session.query(PaymentModel)
                .filter(PaymentModel.user_id == user_id)
                .order_by(PaymentModel.created_at.desc())
                .all()
            )
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch user payments: {exc}") from exc
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            order_id=model.order_id,
            user_id=model.user_id,
            amount=model.amount,
            currency=model.currency,
            method=PaymentMethod(model.method),
            status=PaymentStatus(model.status),
            provider_reference=model.provider_reference,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
