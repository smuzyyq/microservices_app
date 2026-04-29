from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from domain.entities import Order, OrderItem, OrderStatus
from domain.exceptions import DatabaseConnectionError, OrderNotFoundError
from infrastructure.models import OrderItemModel, OrderModel


class IOrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: UUID) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_user(self, user_id: UUID) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def find_by_restaurant(self, restaurant_id: UUID) -> list[Order]:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, id: UUID, status: OrderStatus) -> Order:
        raise NotImplementedError

    @abstractmethod
    def save_item(self, item: OrderItem) -> OrderItem:
        raise NotImplementedError


class OrderRepository(IOrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, order: Order) -> Order:
        try:
            order_model = OrderModel(
                id=order.id,
                user_id=order.user_id,
                restaurant_id=order.restaurant_id,
                status=order.status,
                total_price=order.total_price,
                delivery_address=order.delivery_address,
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
            self.session.add(order_model)
            for item in order.items:
                self.session.add(
                    OrderItemModel(
                        id=item.id,
                        order_id=item.order_id,
                        dish_id=item.dish_id,
                        dish_name=item.dish_name,
                        quantity=item.quantity,
                        price=item.price,
                    )
                )
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            raise DatabaseConnectionError(f"Failed to save order: {exc}") from exc
        return self.find_by_id(order.id)  # type: ignore[return-value]

    def find_by_id(self, id: UUID) -> Order | None:
        try:
            model = (
                self.session.query(OrderModel)
                .options(selectinload(OrderModel.items))
                .filter(OrderModel.id == id)
                .first()
            )
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch order by id: {exc}") from exc
        return self._to_order_entity(model) if model else None

    def find_by_user(self, user_id: UUID) -> list[Order]:
        try:
            models = (
                self.session.query(OrderModel)
                .options(selectinload(OrderModel.items))
                .filter(OrderModel.user_id == user_id)
                .order_by(OrderModel.created_at.desc())
                .all()
            )
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch user orders: {exc}") from exc
        return [self._to_order_entity(model) for model in models]

    def find_by_restaurant(self, restaurant_id: UUID) -> list[Order]:
        try:
            models = (
                self.session.query(OrderModel)
                .options(selectinload(OrderModel.items))
                .filter(OrderModel.restaurant_id == restaurant_id)
                .order_by(OrderModel.created_at.desc())
                .all()
            )
        except Exception as exc:
            raise DatabaseConnectionError(f"Failed to fetch restaurant orders: {exc}") from exc
        return [self._to_order_entity(model) for model in models]

    def update_status(self, id: UUID, status: OrderStatus) -> Order:
        try:
            model = (
                self.session.query(OrderModel)
                .options(selectinload(OrderModel.items))
                .filter(OrderModel.id == id)
                .first()
            )
            if model is None:
                raise OrderNotFoundError("Order not found.")
            model.status = status
            model.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(model)
        except OrderNotFoundError:
            raise
        except Exception as exc:
            self.session.rollback()
            raise DatabaseConnectionError(f"Failed to update order status: {exc}") from exc
        return self._to_order_entity(model)

    def save_item(self, item: OrderItem) -> OrderItem:
        try:
            model = OrderItemModel(
                id=item.id,
                order_id=item.order_id,
                dish_id=item.dish_id,
                dish_name=item.dish_name,
                quantity=item.quantity,
                price=item.price,
            )
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
        except Exception as exc:
            self.session.rollback()
            raise DatabaseConnectionError(f"Failed to save order item: {exc}") from exc
        return self._to_item_entity(model)

    @staticmethod
    def _to_item_entity(model: OrderItemModel) -> OrderItem:
        return OrderItem(
            id=model.id,
            order_id=model.order_id,
            dish_id=model.dish_id,
            dish_name=model.dish_name,
            quantity=model.quantity,
            price=model.price,
        )

    @classmethod
    def _to_order_entity(cls, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            restaurant_id=model.restaurant_id,
            status=model.status,
            total_price=model.total_price,
            delivery_address=model.delivery_address,
            items=[cls._to_item_entity(item) for item in model.items],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
