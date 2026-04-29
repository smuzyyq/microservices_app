from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import User
from infrastructure.models import UserModel


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError


class UserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, user: User) -> User:
        existing_model = self.session.get(UserModel, user.id)
        if existing_model is None:
            model = UserModel(
                id=user.id,
                email=user.email,
                hashed_password=user.hashed_password,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            self.session.add(model)
        else:
            existing_model.email = user.email
            existing_model.hashed_password = user.hashed_password
            existing_model.full_name = user.full_name
            existing_model.role = user.role
            existing_model.is_active = user.is_active
            model = existing_model

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_email(self, email: str) -> User | None:
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def find_by_id(self, user_id: UUID) -> User | None:
        model = self.session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
        )
