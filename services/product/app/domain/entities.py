from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Restaurant:
    id: UUID
    name: str
    description: str
    address: str
    cuisine_type: str
    rating: float
    is_open: bool
    image_url: str | None
    created_at: datetime


@dataclass
class Dish:
    id: UUID
    restaurant_id: UUID
    name: str
    description: str
    price: float
    category: str
    is_available: bool
    image_url: str | None
