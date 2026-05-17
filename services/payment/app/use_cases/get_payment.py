from uuid import UUID

from domain.entities import Payment
from domain.exceptions import PaymentNotFoundError
from interfaces.repositories.payment_repository import IPaymentRepository


class GetPaymentUseCase:
    def __init__(self, payment_repo: IPaymentRepository) -> None:
        self.payment_repo = payment_repo

    def by_id(self, payment_id: UUID) -> Payment:
        payment = self.payment_repo.find_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError("Payment not found.")
        return payment

    def by_order_id(self, order_id: UUID) -> Payment:
        payment = self.payment_repo.find_by_order_id(order_id)
        if payment is None:
            raise PaymentNotFoundError("Payment not found for this order.")
        return payment


class ListUserPaymentsUseCase:
    def __init__(self, payment_repo: IPaymentRepository) -> None:
        self.payment_repo = payment_repo

    def execute(self, user_id: UUID) -> list[Payment]:
        return self.payment_repo.find_by_user(user_id)
