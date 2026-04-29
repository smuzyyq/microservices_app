from datetime import datetime
from uuid import uuid4

from domain.entities import Order, OrderItem, OrderStatus
from interfaces.repositories.order_repository import IOrderRepository


class CreateOrderUseCase:
    def __init__(self, order_repo: IOrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, user_id, restaurant_id, delivery_address: str, items: list[dict]) -> Order:
        created_at = datetime.utcnow()
        order_id = uuid4()
        order_items: list[OrderItem] = []
        total_price = 0.0

        for item in items:
            quantity = int(item["quantity"])
            price = float(item["price"])
            total_price += quantity * price
            order_items.append(
                OrderItem(
                    id=uuid4(),
                    order_id=order_id,
                    dish_id=item["dish_id"],
                    dish_name=item["dish_name"],
                    quantity=quantity,
                    price=price,
                )
            )

        order = Order(
            id=order_id,
            user_id=user_id,
            restaurant_id=restaurant_id,
            status=OrderStatus.pending,
            total_price=round(total_price, 2),
            delivery_address=delivery_address,
            items=order_items,
            created_at=created_at,
            updated_at=created_at,
        )
        return self.order_repo.save(order)
