from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from config import settings
from domain.entities import ChatRoom, Message, SenderRole
from domain.exceptions import RoomAlreadyExistsError, RoomNotFoundError, UnauthorizedError
from infrastructure.database import get_db
from interfaces.repositories.chat_repository import ChatRepository, IChatRepository
from interfaces.schemas.chat_schemas import MessageCreate, MessageResponse, RoomCreate, RoomResponse
from use_cases.create_room import CreateRoomUseCase
from use_cases.get_messages import GetMessagesUseCase
from use_cases.mark_read import MarkReadUseCase
from use_cases.send_message import SendMessageUseCase

router = APIRouter(tags=["chat"])


def get_chat_repository(db: Session = Depends(get_db)) -> IChatRepository:
    return ChatRepository(db)


async def verify_jwt(authorization: str = Header(..., alias="Authorization")) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.auth_verify_url,
            headers={"Authorization": authorization},
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    return response.json()


async def get_order_payload(order_id: UUID, authorization: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.order_service_url}/{order_id}",
                headers={"Authorization": authorization},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order service is unavailable.",
        ) from exc

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to validate order before creating chat room.",
        )
    return response.json()


def _to_room_response(room: ChatRoom) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        order_id=room.order_id,
        customer_id=room.customer_id,
        courier_id=room.courier_id,
        is_active=room.is_active,
        created_at=room.created_at,
    )


def _to_message_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        room_id=message.room_id,
        sender_id=message.sender_id,
        sender_role=message.sender_role,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
    )


def _raise_http_error(error: Exception) -> None:
    if isinstance(error, RoomAlreadyExistsError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    if isinstance(error, RoomNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    if isinstance(error, UnauthorizedError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected chat error.") from error


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreate,
    authorization: str = Header(..., alias="Authorization"),
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> RoomResponse:
    if auth_payload.get("role") not in {"admin", "support"} and UUID(str(auth_payload["user_id"])) != payload.customer_id:
        _raise_http_error(UnauthorizedError("You cannot create a room for another customer."))

    order_payload = await get_order_payload(payload.order_id, authorization)
    order_customer_id = UUID(str(order_payload["user_id"]))
    if order_customer_id != payload.customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected customer does not match the order owner.",
        )

    try:
        room = CreateRoomUseCase(chat_repo).execute(payload.order_id, payload.customer_id)
    except RoomAlreadyExistsError as exc:
        _raise_http_error(exc)
    return _to_room_response(room)


@router.get("/rooms/{order_id}", response_model=RoomResponse)
def get_room_by_order(
    order_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> RoomResponse:
    room = chat_repo.find_room_by_order(order_id)
    if room is None:
        _raise_http_error(RoomNotFoundError("Chat room not found."))
    role = auth_payload.get("role")
    if role in {"courier", "admin", "support"}:
        return _to_room_response(room)
    user_id = UUID(str(auth_payload["user_id"]))
    if user_id not in {room.customer_id, room.courier_id}:
        _raise_http_error(UnauthorizedError("You are not part of this room."))
    return _to_room_response(room)


@router.post("/rooms/{room_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: UUID,
    payload: MessageCreate,
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> MessageResponse:
    try:
        message = SendMessageUseCase(chat_repo).execute(
            room_id=room_id,
            sender_id=UUID(str(auth_payload["user_id"])),
            sender_role=SenderRole(auth_payload["role"]),
            content=payload.content,
        )
    except (RoomNotFoundError, UnauthorizedError, ValueError) as exc:
        _raise_http_error(exc if not isinstance(exc, ValueError) else UnauthorizedError("Unsupported sender role."))
    return _to_message_response(message)


@router.get("/rooms/{room_id}/messages", response_model=list[MessageResponse])
def list_messages(
    room_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> list[MessageResponse]:
    try:
        messages = GetMessagesUseCase(chat_repo).execute(room_id, UUID(str(auth_payload["user_id"])), skip, limit)
    except (RoomNotFoundError, UnauthorizedError) as exc:
        _raise_http_error(exc)
    return [_to_message_response(message) for message in messages]


@router.patch("/rooms/{room_id}/read")
def mark_read(
    room_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> dict[str, int]:
    try:
        marked_count = MarkReadUseCase(chat_repo).execute(room_id, UUID(str(auth_payload["user_id"])))
    except (RoomNotFoundError, UnauthorizedError) as exc:
        _raise_http_error(exc)
    return {"marked_read": marked_count}


@router.patch("/rooms/{room_id}/claim", response_model=RoomResponse)
def claim_room(
    room_id: UUID,
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> RoomResponse:
    if auth_payload.get("role") not in {"courier", "admin"}:
        _raise_http_error(UnauthorizedError("Only courier or admin can claim delivery chats."))

    room = chat_repo.find_room_by_id(room_id)
    if room is None:
        _raise_http_error(RoomNotFoundError("Chat room not found."))

    courier_id = UUID(str(auth_payload["user_id"]))
    if room.courier_id not in {None, courier_id}:
        _raise_http_error(UnauthorizedError("This chat room is already assigned to another courier."))

    claimed_room = chat_repo.assign_courier(room_id, courier_id)
    return _to_room_response(claimed_room)


@router.get("/my-rooms", response_model=list[RoomResponse])
def my_rooms(
    auth_payload: dict = Depends(verify_jwt),
    chat_repo: IChatRepository = Depends(get_chat_repository),
) -> list[RoomResponse]:
    rooms = chat_repo.get_user_rooms(UUID(str(auth_payload["user_id"])))
    return [_to_room_response(room) for room in rooms]
