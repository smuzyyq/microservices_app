from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import Payment, PaymentMethod, PaymentStatus
from domain.exceptions import DatabaseConnectionError, PaymentNotFoundError, UnauthorizedError
from infrastructure.database import get_db
from interfaces.repositories.payment_repository import IPaymentRepository, PaymentRepository
from interfaces.schemas.payment_schemas import PaymentCreate, PaymentResponse
from use_cases.create_payment import CreatePaymentUseCase
from use_cases.get_payment import GetPaymentUseCase, ListUserPaymentsUseCase

router = APIRouter(tags=["payments"])


def get_payment_repository(db: Session = Depends(get_db)) -> IPaymentRepository:
    return PaymentRepository(db)


async def verify_jwt(authorization: str = Header(..., alias="Authorization")) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    return response.json()


def _to_payment_response(payment: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        amount=payment.amount,
        currency=payment.currency,
        method=payment.method,
        status=payment.status,
        provider_reference=payment.provider_reference,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, PaymentNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, UnauthorizedError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    if isinstance(error, DatabaseConnectionError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected payment error.") from error


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    auth_payload: dict = Depends(verify_jwt),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
) -> PaymentResponse:
    try:
        payment = CreatePaymentUseCase(payment_repo).execute(
            order_id=payload.order_id,
            user_id=UUID(str(auth_payload["user_id"])),
            amount=payload.amount,
            currency=payload.currency,
            method=payload.method,
        )
    except DatabaseConnectionError as exc:
        _raise_http_error(exc)
    return _to_payment_response(payment)


@router.get("/my", response_model=list[PaymentResponse])
def list_my_payments(
    auth_payload: dict = Depends(verify_jwt),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
) -> list[PaymentResponse]:
    try:
        payments = ListUserPaymentsUseCase(payment_repo).execute(UUID(str(auth_payload["user_id"])))
    except DatabaseConnectionError as exc:
        _raise_http_error(exc)
    return [_to_payment_response(payment) for payment in payments]


@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_order(
    order_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
) -> PaymentResponse:
    try:
        payment = GetPaymentUseCase(payment_repo).by_order_id(order_id)
        role = auth_payload.get("role")
        if role not in {"admin", "support", "courier"} and payment.user_id != UUID(str(auth_payload["user_id"])):
            raise UnauthorizedError("You are not allowed to view this payment.")
    except (PaymentNotFoundError, UnauthorizedError, DatabaseConnectionError) as exc:
        _raise_http_error(exc)
    return _to_payment_response(payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    payment_repo: IPaymentRepository = Depends(get_payment_repository),
) -> PaymentResponse:
    try:
        payment = GetPaymentUseCase(payment_repo).by_id(payment_id)
        role = auth_payload.get("role")
        if role not in {"admin", "support"} and payment.user_id != UUID(str(auth_payload["user_id"])):
            raise UnauthorizedError("You are not allowed to view this payment.")
    except (PaymentNotFoundError, UnauthorizedError, DatabaseConnectionError) as exc:
        _raise_http_error(exc)
    return _to_payment_response(payment)
