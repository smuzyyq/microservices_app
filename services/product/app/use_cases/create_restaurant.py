from datetime import datetime
from uuid import uuid4

from domain.entities import Restaurant
from interfaces.repositories.product_repository import IProductRepository


class CreateRestaurantUseCase:
    def __init__(self, product_repo: IProductRepository) -> None:
        self.product_repo = product_repo

    def execute(self, name: str, description: str, address: str, cuisine_type: str) -> Restaurant:
        restaurant = Restaurant(
            id=uuid4(),
            name=name,
            description=description,
            address=address,
            cuisine_type=cuisine_type,
            rating=0.0,
            is_open=True,
            image_url=None,
            created_at=datetime.utcnow(),
        )
        return self.product_repo.save_restaurant(restaurant)
