from domain.entities import Restaurant
from interfaces.repositories.product_repository import IProductRepository


class GetRestaurantsUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self, skip: int, limit: int) -> list[Restaurant]:
        return self.product_repo.get_all_restaurants(skip=skip, limit=limit)
