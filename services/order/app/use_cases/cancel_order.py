from domain.entities import Order, OrderStatus
from domain.exceptions import InvalidStatusTransitionError, OrderNotFoundError, UnauthorizedError
from interfaces.repositories.order_repository import IOrderRepository


class CancelOrderUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, order_id, user_id) -> Order:
        order = self.order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found.")
        if order.user_id != user_id:
            raise UnauthorizedError("You are not allowed to cancel this order.")
        if order.status != OrderStatus.pending:
            raise InvalidStatusTransitionError("Only pending orders can be cancelled.")
        return self.order_repo.update_status(order_id, OrderStatus.cancelled)
