from domain.entities import Dish
from interfaces.repositories.product_repository import IProductRepository


class SearchDishesUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self, query: str) -> list[Dish]:
        return self.product_repo.search_dishes(query)
