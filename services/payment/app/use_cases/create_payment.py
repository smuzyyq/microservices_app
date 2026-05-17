from datetime import datetime
from uuid import UUID, uuid4

from domain.entities import Payment, PaymentMethod, PaymentStatus
from interfaces.repositories.payment_repository import IPaymentRepository


class CreatePaymentUseCase:
    def __init__(self, payment_repo: IPaymentRepository) -> None:
        self.payment_repo = payment_repo

    def execute(
        self,
        order_id: UUID,
        user_id: UUID,
        amount: float,
        currency: str,
        method: PaymentMethod,
    ) -> Payment:
        existing = self.payment_repo.find_by_order_id(order_id)
        if existing is not None:
            return existing

        created_at = datetime.utcnow()
        payment = Payment(
            id=uuid4(),
            order_id=order_id,
            user_id=user_id,
            amount=round(amount, 2),
            currency=currency.upper(),
            method=method,
            status=PaymentStatus.succeeded,
            provider_reference=f"demo_{uuid4().hex[:12]}",
            created_at=created_at,
            updated_at=created_at,
        )
        return self.payment_repo.save(payment)
