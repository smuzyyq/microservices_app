from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Order
from domain.exceptions import (
    DatabaseConnectionError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
    UnauthorizedError,
)
from infrastructure.database import get_db
from interfaces.repositories.order_repository import IOrderRepository, OrderRepository
from interfaces.schemas.order_schemas import OrderCreate, OrderItemResponse, OrderResponse, OrderStatusUpdate
from use_cases.cancel_order import CancelOrderUseCase
from use_cases.create_order import CreateOrderUseCase
from use_cases.get_order import GetOrderUseCase
from use_cases.update_status import UpdateOrderStatusUseCase

router = APIRouter(tags=["orders"])


def get_order_repository(db: Session = Depends(get_db)) -> IOrderRepository:
    return OrderRepository(db)


async def verify_jwt(authorization: str = Header(..., alias="Authorization")) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    return response.json()


async def _fetch_product_resource(path: str) -> dict:
    url = f"{settings.product_service_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Product service is unavailable.",
        ) from exc

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found.")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to validate order items against product service.",
        )
    return response.json()


async def _validate_order_items(restaurant_id: UUID, items: list[dict]) -> list[dict]:
    validated_items: list[dict] = []

    try:
        await _fetch_product_resource(f"/restaurants/{restaurant_id}")
    except HTTPException as exc:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.") from exc
        raise

    for item in items:
        try:
            dish = await _fetch_product_resource(f"/dishes/{item['dish_id']}")
        except HTTPException as exc:
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found.") from exc
            raise

        if UUID(str(dish["restaurant_id"])) != restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All dishes in the order must belong to the selected restaurant.",
            )
        if not dish["is_available"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dish '{dish['name']}' is currently unavailable.",
            )

        validated_items.append(
            {
                "dish_id": UUID(str(dish["id"])),
                "dish_name": dish["name"],
                "quantity": item["quantity"],
                "price": dish["price"],
            }
        )

    return validated_items


def _to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        status=order.status,
        total_price=order.total_price,
        delivery_address=order.delivery_address,
        items=[
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                dish_id=item.dish_id,
                dish_name=item.dish_name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, OrderNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, UnauthorizedError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    if isinstance(error, InvalidStatusTransitionError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    if isinstance(error, DatabaseConnectionError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected order error.") from error


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> OrderResponse:
    try:
        validated_items = await _validate_order_items(
            restaurant_id=payload.restaurant_id,
            items=[item.model_dump() for item in payload.items],
        )
        order = CreateOrderUseCase(order_repo).execute(
            user_id=UUID(str(auth_payload["user_id"])),
            restaurant_id=payload.restaurant_id,
            delivery_address=payload.delivery_address,
            items=validated_items,
        )
    except (DatabaseConnectionError,) as exc:
        _raise_http_error(exc)
    return _to_order_response(order)


@router.get("", response_model=list[OrderResponse])
def list_user_orders(
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> list[OrderResponse]:
    try:
        orders = order_repo.find_by_user(UUID(str(auth_payload["user_id"])))
    except DatabaseConnectionError as exc:
        _raise_http_error(exc)
    return [_to_order_response(order) for order in orders]


@router.get("/restaurant/{restaurant_id}", response_model=list[OrderResponse])
def list_restaurant_orders(
    restaurant_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> list[OrderResponse]:
    if auth_payload.get("role") not in {"courier", "admin"}:
        _raise_http_error(UnauthorizedError("Only courier or admin can access restaurant orders."))
    try:
        orders = order_repo.find_by_restaurant(restaurant_id)
    except DatabaseConnectionError as exc:
        _raise_http_error(exc)
    return [_to_order_response(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> OrderResponse:
    role = auth_payload.get("role")
    try:
        if role in {"courier", "admin", "support"}:
            order = order_repo.find_by_id(order_id)
            if order is None:
                raise OrderNotFoundError("Order not found.")
        else:
            order = GetOrderUseCase(order_repo).execute(order_id, UUID(str(auth_payload["user_id"])))
    except (OrderNotFoundError, UnauthorizedError, DatabaseConnectionError) as exc:
        _raise_http_error(exc)
    return _to_order_response(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> OrderResponse:
    try:
        order = UpdateOrderStatusUseCase(order_repo).execute(order_id, payload.status, auth_payload.get("role", ""))
    except (
        OrderNotFoundError,
        UnauthorizedError,
        InvalidStatusTransitionError,
        DatabaseConnectionError,
    ) as exc:
        _raise_http_error(exc)
    return _to_order_response(order)


@router.delete("/{order_id}", response_model=OrderResponse)
def cancel_order(
    order_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    order_repo: IOrderRepository = Depends(get_order_repository),
) -> OrderResponse:
    try:
        order = CancelOrderUseCase(order_repo).execute(order_id, UUID(str(auth_payload["user_id"])))
    except (
        OrderNotFoundError,
        UnauthorizedError,
        InvalidStatusTransitionError,
        DatabaseConnectionError,
    ) as exc:
        _raise_http_error(exc)
    return _to_order_response(order)
