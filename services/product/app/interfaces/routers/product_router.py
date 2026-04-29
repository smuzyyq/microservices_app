from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Dish, Restaurant
from domain.exceptions import DishNotFoundError, RestaurantNotFoundError, UnauthorizedError
from infrastructure.database import get_db
from interfaces.repositories.product_repository import IProductRepository, ProductRepository
from interfaces.schemas.product_schemas import (
    DishAvailabilityUpdate,
    DishCreate,
    DishResponse,
    MenuResponse,
    RestaurantCreate,
    RestaurantResponse,
    SearchResponse,
)
from use_cases.create_dish import CreateDishUseCase
from use_cases.create_restaurant import CreateRestaurantUseCase
from use_cases.get_menu import GetMenuUseCase
from use_cases.get_restaurants import GetRestaurantsUseCase
from use_cases.search_dishes import SearchDishesUseCase

router = APIRouter(tags=["products"])


def get_product_repository(db: Session = Depends(get_db)) -> IProductRepository:
    return ProductRepository(db)


async def verify_jwt(authorization: str = Header(...)) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    return response.json()


def require_admin(auth_payload: dict = Depends(verify_jwt)) -> dict:
    if auth_payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin access required.")
    return auth_payload


def _to_restaurant_response(restaurant: Restaurant) -> RestaurantResponse:
    return RestaurantResponse(
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


def _to_dish_response(dish: Dish) -> DishResponse:
    return DishResponse(
        id=dish.id,
        restaurant_id=dish.restaurant_id,
        name=dish.name,
        description=dish.description,
        price=dish.price,
        category=dish.category,
        is_available=dish.is_available,
        image_url=dish.image_url,
    )


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, RestaurantNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, DishNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, UnauthorizedError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected product error.") from error


@router.get("/restaurants", response_model=list[RestaurantResponse])
def list_restaurants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    product_repo: IProductRepository = Depends(get_product_repository),
) -> list[RestaurantResponse]:
    restaurants = GetRestaurantsUseCase(product_repo).execute(skip=skip, limit=limit)
    return [_to_restaurant_response(restaurant) for restaurant in restaurants]


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: UUID,
    product_repo: IProductRepository = Depends(get_product_repository),
) -> RestaurantResponse:
    restaurant = product_repo.get_restaurant_by_id(restaurant_id)
    if restaurant is None:
        _raise_http_error(RestaurantNotFoundError("Restaurant not found."))
    return _to_restaurant_response(restaurant)


@router.get("/restaurants/{restaurant_id}/menu", response_model=MenuResponse)
def get_menu(
    restaurant_id: UUID,
    product_repo: IProductRepository = Depends(get_product_repository),
) -> MenuResponse:
    try:
        restaurant, dishes = GetMenuUseCase(product_repo).execute(restaurant_id)
    except RestaurantNotFoundError as exc:
        _raise_http_error(exc)
    return MenuResponse(
        restaurant=_to_restaurant_response(restaurant),
        dishes=[_to_dish_response(dish) for dish in dishes],
    )


@router.get("/dishes/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: UUID,
    product_repo: IProductRepository = Depends(get_product_repository),
) -> DishResponse:
    dish = product_repo.get_dish_by_id(dish_id)
    if dish is None:
        _raise_http_error(DishNotFoundError("Dish not found."))
    return _to_dish_response(dish)


@router.post("/restaurants", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate,
    product_repo: IProductRepository = Depends(get_product_repository),
    _: dict = Depends(require_admin),
) -> RestaurantResponse:
    restaurant = CreateRestaurantUseCase(product_repo).execute(
        name=payload.name,
        description=payload.description,
        address=payload.address,
        cuisine_type=payload.cuisine_type,
    )
    return _to_restaurant_response(restaurant)


@router.post("/dishes", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    payload: DishCreate,
    product_repo: IProductRepository = Depends(get_product_repository),
    _: dict = Depends(require_admin),
) -> DishResponse:
    try:
        dish = CreateDishUseCase(product_repo).execute(
            restaurant_id=payload.restaurant_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            category=payload.category,
            image_url=payload.image_url,
        )
    except RestaurantNotFoundError as exc:
        _raise_http_error(exc)
    return _to_dish_response(dish)


@router.patch("/dishes/{dish_id}/availability", response_model=DishResponse)
def update_dish_availability(
    dish_id: UUID,
    payload: DishAvailabilityUpdate,
    product_repo: IProductRepository = Depends(get_product_repository),
    _: dict = Depends(require_admin),
) -> DishResponse:
    try:
        dish = product_repo.update_dish_availability(dish_id, payload.is_available)
    except DishNotFoundError as exc:
        _raise_http_error(exc)
    return _to_dish_response(dish)


@router.get("/search", response_model=SearchResponse)
def search_dishes(
    q: str = Query(..., min_length=1),
    product_repo: IProductRepository = Depends(get_product_repository),
) -> SearchResponse:
    dishes = SearchDishesUseCase(product_repo).execute(q)
    return SearchResponse(dishes=[_to_dish_response(dish) for dish in dishes])
