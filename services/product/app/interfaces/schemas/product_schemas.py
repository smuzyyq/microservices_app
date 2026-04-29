from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=3, max_length=1000)
    address: str = Field(min_length=3, max_length=255)
    cuisine_type: str = Field(min_length=2, max_length=100)


class RestaurantResponse(BaseModel):
    id: UUID
    name: str
    description: str
    address: str
    cuisine_type: str
    rating: float
    is_open: bool
    image_url: str | None
    created_at: datetime


class DishCreate(BaseModel):
    restaurant_id: UUID
    name: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=3, max_length=1000)
    price: float = Field(gt=0)
    category: str = Field(min_length=2, max_length=100)
    image_url: str | None = None


class DishResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    description: str
    price: float
    category: str
    is_available: bool
    image_url: str | None


class MenuResponse(BaseModel):
    restaurant: RestaurantResponse
    dishes: list[DishResponse]


class SearchResponse(BaseModel):
    dishes: list[DishResponse]


class DishAvailabilityUpdate(BaseModel):
    is_available: bool
