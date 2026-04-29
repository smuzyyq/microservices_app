from domain.entities import Order, OrderStatus
from domain.exceptions import InvalidStatusTransitionError, OrderNotFoundError, UnauthorizedError
from interfaces.repositories.order_repository import IOrderRepository

VALID_TRANSITIONS = {
    OrderStatus.pending: {OrderStatus.confirmed, OrderStatus.cancelled},
    OrderStatus.confirmed: {OrderStatus.preparing, OrderStatus.cancelled},
    OrderStatus.preparing: {OrderStatus.delivering},
    OrderStatus.delivering: {OrderStatus.delivered},
    OrderStatus.delivered: set(),
    OrderStatus.cancelled: set(),
}


class UpdateOrderStatusUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, order_id, new_status: OrderStatus, requester_role: str) -> Order:
        if requester_role not in {"courier", "admin"}:
            raise UnauthorizedError("Only courier or admin can update order status.")

        order = self.order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found.")

        if new_status not in VALID_TRANSITIONS[order.status]:
            raise InvalidStatusTransitionError(
                f"Cannot change order status from '{order.status.value}' to '{new_status.value}'."
            )

        return self.order_repo.update_status(order_id, new_status)
