from domain.entities import Order
from domain.exceptions import OrderNotFoundError, UnauthorizedError
from interfaces.repositories.order_repository import IOrderRepository


class GetOrderUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, order_id, user_id) -> Order:
        order = self.order_repo.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found.")
        if order.user_id != user_id:
            raise UnauthorizedError("You are not allowed to access this order.")
        return order
