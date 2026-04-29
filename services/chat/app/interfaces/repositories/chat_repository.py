from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import ChatRoom, Message
from infrastructure.models import ChatRoomModel, MessageModel


class IChatRepository(ABC):
    @abstractmethod
    def save_room(self, room: ChatRoom) -> ChatRoom:
        raise NotImplementedError

    @abstractmethod
    def find_room_by_order(self, order_id: UUID) -> ChatRoom | None:
        raise NotImplementedError

    @abstractmethod
    def find_room_by_id(self, id: UUID) -> ChatRoom | None:
        raise NotImplementedError

    @abstractmethod
    def get_user_rooms(self, user_id: UUID) -> list[ChatRoom]:
        raise NotImplementedError

    @abstractmethod
    def save_message(self, message: Message) -> Message:
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, room_id: UUID, skip: int, limit: int) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def mark_messages_read(self, room_id: UUID, reader_id: UUID) -> int:
        raise NotImplementedError

    @abstractmethod
    def assign_courier(self, room_id: UUID, courier_id: UUID) -> ChatRoom:
        raise NotImplementedError


class ChatRepository(IChatRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_room(self, room: ChatRoom) -> ChatRoom:
        model = ChatRoomModel(
            id=room.id,
            order_id=room.order_id,
            customer_id=room.customer_id,
            courier_id=room.courier_id,
            is_active=room.is_active,
            created_at=room.created_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_room_entity(model)

    def find_room_by_order(self, order_id: UUID) -> ChatRoom | None:
        model = self.session.query(ChatRoomModel).filter(ChatRoomModel.order_id == order_id).first()
        return self._to_room_entity(model) if model else None

    def find_room_by_id(self, id: UUID) -> ChatRoom | None:
        model = self.session.get(ChatRoomModel, id)
        return self._to_room_entity(model) if model else None

    def get_user_rooms(self, user_id: UUID) -> list[ChatRoom]:
        models = (
            self.session.query(ChatRoomModel)
            .filter(
                (ChatRoomModel.customer_id == user_id)
                | (ChatRoomModel.courier_id == user_id)
            )
            .order_by(ChatRoomModel.created_at.desc())
            .all()
        )
        return [self._to_room_entity(model) for model in models]

    def save_message(self, message: Message) -> Message:
        model = MessageModel(
            id=message.id,
            room_id=message.room_id,
            sender_id=message.sender_id,
            sender_role=message.sender_role,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_message_entity(model)

    def get_messages(self, room_id: UUID, skip: int, limit: int) -> list[Message]:
        models = (
            self.session.query(MessageModel)
            .filter(MessageModel.room_id == room_id)
            .order_by(MessageModel.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_message_entity(model) for model in models]

    def mark_messages_read(self, room_id: UUID, reader_id: UUID) -> int:
        updated = (
            self.session.query(MessageModel)
            .filter(
                MessageModel.room_id == room_id,
                MessageModel.sender_id != reader_id,
                MessageModel.is_read.is_(False),
            )
            .update({"is_read": True}, synchronize_session=False)
        )
        self.session.commit()
        return updated

    def assign_courier(self, room_id: UUID, courier_id: UUID) -> ChatRoom:
        model = self.session.get(ChatRoomModel, room_id)
        if model is None:
            raise ValueError("Chat room not found.")

        model.courier_id = courier_id
        self.session.commit()
        self.session.refresh(model)
        return self._to_room_entity(model)

    @staticmethod
    def _to_room_entity(model: ChatRoomModel) -> ChatRoom:
        return ChatRoom(
            id=model.id,
            order_id=model.order_id,
            customer_id=model.customer_id,
            courier_id=model.courier_id,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_message_entity(model: MessageModel) -> Message:
        return Message(
            id=model.id,
            room_id=model.room_id,
            sender_id=model.sender_id,
            sender_role=model.sender_role,
            content=model.content,
            is_read=model.is_read,
            created_at=model.created_at,
        )
