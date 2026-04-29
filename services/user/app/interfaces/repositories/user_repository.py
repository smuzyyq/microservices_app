from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import DeliveryAddress, UserProfile
from infrastructure.models import DeliveryAddressModel, UserProfileModel


class IUserRepository(ABC):
    @abstractmethod
    def get_profile(self, user_id: UUID) -> UserProfile | None:
        raise NotImplementedError

    @abstractmethod
    def save_profile(self, profile: UserProfile) -> UserProfile:
        raise NotImplementedError

    @abstractmethod
    def get_addresses(self, user_id: UUID) -> list[DeliveryAddress]:
        raise NotImplementedError

    @abstractmethod
    def get_address_by_id(self, id: UUID) -> DeliveryAddress | None:
        raise NotImplementedError

    @abstractmethod
    def save_address(self, address: DeliveryAddress) -> DeliveryAddress:
        raise NotImplementedError

    @abstractmethod
    def delete_address(self, id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def unset_default_addresses(self, user_id: UUID) -> None:
        raise NotImplementedError


class UserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_profile(self, user_id: UUID) -> UserProfile | None:
        model = self.session.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
        return self._to_profile_entity(model) if model else None

    def save_profile(self, profile: UserProfile) -> UserProfile:
        model = self.session.query(UserProfileModel).filter(UserProfileModel.user_id == profile.user_id).first()
        if model is None:
            model = UserProfileModel(
                id=profile.id,
                user_id=profile.user_id,
                phone=profile.phone,
                avatar_url=profile.avatar_url,
                default_address=profile.default_address,
            )
            self.session.add(model)
        else:
            model.phone = profile.phone
            model.avatar_url = profile.avatar_url
            model.default_address = profile.default_address

        self.session.commit()
        self.session.refresh(model)
        return self._to_profile_entity(model)

    def get_addresses(self, user_id: UUID) -> list[DeliveryAddress]:
        models = (
            self.session.query(DeliveryAddressModel)
            .filter(DeliveryAddressModel.user_id == user_id)
            .order_by(DeliveryAddressModel.is_default.desc(), DeliveryAddressModel.label.asc())
            .all()
        )
        return [self._to_address_entity(model) for model in models]

    def get_address_by_id(self, id: UUID) -> DeliveryAddress | None:
        model = self.session.get(DeliveryAddressModel, id)
        return self._to_address_entity(model) if model else None

    def save_address(self, address: DeliveryAddress) -> DeliveryAddress:
        model = DeliveryAddressModel(
            id=address.id,
            user_id=address.user_id,
            label=address.label,
            full_address=address.full_address,
            is_default=address.is_default,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_address_entity(model)

    def delete_address(self, id: UUID) -> bool:
        model = self.session.get(DeliveryAddressModel, id)
        if model is None:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def unset_default_addresses(self, user_id: UUID) -> None:
        self.session.query(DeliveryAddressModel).filter(DeliveryAddressModel.user_id == user_id).update(
            {"is_default": False}
        )
        self.session.commit()

    @staticmethod
    def _to_profile_entity(model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            user_id=model.user_id,
            phone=model.phone,
            avatar_url=model.avatar_url,
            default_address=model.default_address,
        )

    @staticmethod
    def _to_address_entity(model: DeliveryAddressModel) -> DeliveryAddress:
        return DeliveryAddress(
            id=model.id,
            user_id=model.user_id,
            label=model.label,
            full_address=model.full_address,
            is_default=model.is_default,
        )
