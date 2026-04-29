from datetime import datetime
from uuid import uuid4

from domain.entities import Message, SenderRole
from domain.exceptions import RoomNotFoundError, UnauthorizedError
from interfaces.repositories.chat_repository import IChatRepository


class SendMessageUseCase:
    def __init__(self, chat_repo: IChatRepository) -> None:
        self.chat_repo = chat_repo

    def execute(self, room_id, sender_id, sender_role: SenderRole, content: str) -> Message:
        room = self.chat_repo.find_room_by_id(room_id)
        if room is None:
            raise RoomNotFoundError("Chat room not found.")
        if sender_role == SenderRole.customer and room.customer_id != sender_id:
            raise UnauthorizedError("Customer is not part of this room.")
        if sender_role == SenderRole.courier and room.courier_id != sender_id:
            raise UnauthorizedError("Courier is not assigned to this room.")

        message = Message(
            id=uuid4(),
            room_id=room_id,
            sender_id=sender_id,
            sender_role=sender_role,
            content=content,
            is_read=False,
            created_at=datetime.utcnow(),
        )
        return self.chat_repo.save_message(message)
