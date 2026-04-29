from domain.entities import Dish, Restaurant
from domain.exceptions import RestaurantNotFoundError
from interfaces.repositories.product_repository import IProductRepository


class GetMenuUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self, restaurant_id) -> tuple[Restaurant, list[Dish]]:
        restaurant = self.product_repo.get_restaurant_by_id(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError("Restaurant not found.")
        dishes = self.product_repo.get_dishes_by_restaurant(restaurant_id)
        return restaurant, dishes
