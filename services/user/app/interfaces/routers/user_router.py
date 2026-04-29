from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import DeliveryAddress, UserProfile
from domain.exceptions import AddressNotFoundError, ProfileNotFoundError, UnauthorizedError
from infrastructure.database import get_db
from interfaces.repositories.user_repository import IUserRepository, UserRepository
from interfaces.schemas.user_schemas import AddressCreate, AddressResponse, ProfileResponse, ProfileUpdate
from use_cases.add_address import AddAddressUseCase
from use_cases.delete_address import DeleteAddressUseCase
from use_cases.get_profile import GetProfileUseCase
from use_cases.update_profile import UpdateProfileUseCase

router = APIRouter(tags=["users"])


def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)


async def verify_jwt(authorization: str = Header(..., alias="Authorization")) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    return response.json()


def _to_profile_response(profile: UserProfile) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        phone=profile.phone,
        avatar_url=profile.avatar_url,
        default_address=profile.default_address,
    )


def _to_address_response(address: DeliveryAddress) -> AddressResponse:
    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        label=address.label,
        full_address=address.full_address,
        is_default=address.is_default,
    )


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, ProfileNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, AddressNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, UnauthorizedError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected user error.") from error


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    auth_payload: dict = Depends(verify_jwt),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> ProfileResponse:
    try:
        profile = GetProfileUseCase(user_repo).execute(UUID(str(auth_payload["user_id"])))
    except ProfileNotFoundError as exc:
        _raise_http_error(exc)
    return _to_profile_response(profile)


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate,
    auth_payload: dict = Depends(verify_jwt),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> ProfileResponse:
    profile = UpdateProfileUseCase(user_repo).execute(
        user_id=UUID(str(auth_payload["user_id"])),
        phone=payload.phone,
        avatar_url=payload.avatar_url,
        default_address=payload.default_address,
    )
    return _to_profile_response(profile)


@router.get("/addresses", response_model=list[AddressResponse])
def list_addresses(
    auth_payload: dict = Depends(verify_jwt),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> list[AddressResponse]:
    addresses = user_repo.get_addresses(UUID(str(auth_payload["user_id"])))
    return [_to_address_response(address) for address in addresses]


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def add_address(
    payload: AddressCreate,
    auth_payload: dict = Depends(verify_jwt),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> AddressResponse:
    address = AddAddressUseCase(user_repo).execute(
        user_id=UUID(str(auth_payload["user_id"])),
        label=payload.label,
        full_address=payload.full_address,
        is_default=payload.is_default,
    )
    return _to_address_response(address)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> None:
    try:
        deleted = DeleteAddressUseCase(user_repo).execute(address_id, UUID(str(auth_payload["user_id"])))
    except (AddressNotFoundError, UnauthorizedError) as exc:
        _raise_http_error(exc)
    if not deleted:
        _raise_http_error(AddressNotFoundError("Address not found."))
