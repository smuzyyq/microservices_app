from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from domain.entities import Dish, Restaurant
from domain.exceptions import DishNotFoundError
from infrastructure.models import DishModel, RestaurantModel


class IProductRepository(ABC):
    @abstractmethod
    def get_all_restaurants(self, skip: int, limit: int) -> list[Restaurant]:
        raise NotImplementedError

    @abstractmethod
    def get_restaurant_by_id(self, id: UUID) -> Restaurant | None:
        raise NotImplementedError

    @abstractmethod
    def get_dishes_by_restaurant(self, restaurant_id: UUID) -> list[Dish]:
        raise NotImplementedError

    @abstractmethod
    def get_dish_by_id(self, id: UUID) -> Dish | None:
        raise NotImplementedError

    @abstractmethod
    def save_restaurant(self, restaurant: Restaurant) -> Restaurant:
        raise NotImplementedError

    @abstractmethod
    def save_dish(self, dish: Dish) -> Dish:
        raise NotImplementedError

    @abstractmethod
    def search_dishes(self, query: str) -> list[Dish]:
        raise NotImplementedError

    @abstractmethod
    def update_dish_availability(self, id: UUID, is_available: bool) -> Dish:
        raise NotImplementedError


class ProductRepository(IProductRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_restaurants(self, skip: int, limit: int) -> list[Restaurant]:
        models = (
            self.session.query(RestaurantModel)
            .order_by(RestaurantModel.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_restaurant_entity(model) for model in models]

    def get_restaurant_by_id(self, id: UUID) -> Restaurant | None:
        model = self.session.get(RestaurantModel, id)
        return self._to_restaurant_entity(model) if model else None

    def get_dishes_by_restaurant(self, restaurant_id: UUID) -> list[Dish]:
        models = (
            self.session.query(DishModel)
            .filter(DishModel.restaurant_id == restaurant_id)
            .order_by(DishModel.category.asc(), DishModel.name.asc())
            .all()
        )
        return [self._to_dish_entity(model) for model in models]

    def get_dish_by_id(self, id: UUID) -> Dish | None:
        model = self.session.get(DishModel, id)
        return self._to_dish_entity(model) if model else None

    def save_restaurant(self, restaurant: Restaurant) -> Restaurant:
        model = RestaurantModel(
            id=restaurant.id,
            name=restaurant.name,
            description=restaurant.description,
            address=restaurant.address,
            cuisine_type=restaurant.cuisine_type,
            rating=restaurant.rating,
            is_open=restaurant.is_open,
            image_url=restaurant.image_url,
            created_at=restaurant.created_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_restaurant_entity(model)

    def save_dish(self, dish: Dish) -> Dish:
        model = DishModel(
            id=dish.id,
            restaurant_id=dish.restaurant_id,
            name=dish.name,
            description=dish.description,
            price=dish.price,
            category=dish.category,
            is_available=dish.is_available,
            image_url=dish.image_url,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_dish_entity(model)

    def search_dishes(self, query: str) -> list[Dish]:
        pattern = f"%{query.strip()}%"
        models = (
            self.session.query(DishModel)
            .filter(
                or_(
                    DishModel.name.ilike(pattern),
                    DishModel.description.ilike(pattern),
                    DishModel.category.ilike(pattern),
                )
            )
            .order_by(DishModel.name.asc())
            .all()
        )
        return [self._to_dish_entity(model) for model in models]

    def update_dish_availability(self, id: UUID, is_available: bool) -> Dish:
        model = self.session.get(DishModel, id)
        if model is None:
            raise DishNotFoundError("Dish not found.")
        model.is_available = is_available
        self.session.commit()
        self.session.refresh(model)
        return self._to_dish_entity(model)

    @staticmethod
    def _to_restaurant_entity(model: RestaurantModel) -> Restaurant:
        return Restaurant(
            id=model.id,
            name=model.name,
            description=model.description,
            address=model.address,
            cuisine_type=model.cuisine_type,
            rating=model.rating,
            is_open=model.is_open,
            image_url=model.image_url,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_dish_entity(model: DishModel) -> Dish:
        return Dish(
            id=model.id,
            restaurant_id=model.restaurant_id,
            name=model.name,
            description=model.description,
            price=model.price,
            category=model.category,
            is_available=model.is_available,
            image_url=model.image_url,
        )
