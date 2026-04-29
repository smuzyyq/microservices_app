from uuid import uuid4

from domain.entities import Dish
from domain.exceptions import RestaurantNotFoundError
from interfaces.repositories.product_repository import IProductRepository


class CreateDishUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(
        self,
        restaurant_id,
        name: str,
        description: str,
        price: float,
        category: str,
        image_url: str | None,
    ) -> Dish:
        restaurant = self.product_repo.get_restaurant_by_id(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError("Restaurant not found.")

        dish = Dish(
            id=uuid4(),
            restaurant_id=restaurant_id,
            name=name,
            description=description,
            price=price,
            category=category,
            is_available=True,
            image_url=image_url,
        )
        return self.product_repo.save_dish(dish)
