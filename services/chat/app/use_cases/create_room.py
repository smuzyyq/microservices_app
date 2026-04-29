from datetime import datetime
from uuid import uuid4

from domain.entities import ChatRoom
from domain.exceptions import RoomAlreadyExistsError
from interfaces.repositories.chat_repository import IChatRepository


class CreateRoomUseCase:
    def __init__(self, chat_repo: IChatRepository) -> None:
        self.chat_repo = chat_repo

    def execute(self, order_id, customer_id) -> ChatRoom:
        existing = self.chat_repo.find_room_by_order(order_id)
        if existing is not None:
            raise RoomAlreadyExistsError("Room for this order already exists.")

        room = ChatRoom(
            id=uuid4(),
            order_id=order_id,
            customer_id=customer_id,
            courier_id=None,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        return self.chat_repo.save_room(room)
