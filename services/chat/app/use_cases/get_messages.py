from domain.entities import Message
from domain.exceptions import RoomNotFoundError, UnauthorizedError
from interfaces.repositories.chat_repository import IChatRepository


class GetMessagesUseCase:
    def __init__(self, chat_repo: IChatRepository) -> None:
        self.chat_repo = chat_repo

    def execute(self, room_id, user_id, skip: int, limit: int) -> list[Message]:
        room = self.chat_repo.find_room_by_id(room_id)
        if room is None:
            raise RoomNotFoundError("Chat room not found.")
        if user_id not in {room.customer_id, room.courier_id}:
            raise UnauthorizedError("You are not part of this room.")
        return self.chat_repo.get_messages(room_id, skip, limit)
