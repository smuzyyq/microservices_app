from uuid import uuid4

from domain.entities import DeliveryAddress, UserProfile
from interfaces.repositories.user_repository import IUserRepository


class AddAddressUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id, label: str, full_address: str, is_default: bool) -> DeliveryAddress:
        profile = self.user_repo.get_profile(user_id)
        if profile is None:
            profile = self.user_repo.save_profile(
                UserProfile(
                    id=uuid4(),
                    user_id=user_id,
                    phone=None,
                    avatar_url=None,
                    default_address=full_address if is_default else None,
                )
            )

        if is_default:
            self.user_repo.unset_default_addresses(user_id)

        address = DeliveryAddress(
            id=uuid4(),
            user_id=user_id,
            label=label,
            full_address=full_address,
            is_default=is_default,
        )
        saved_address = self.user_repo.save_address(address)

        if is_default:
            profile.default_address = full_address
            self.user_repo.save_profile(profile)

        return saved_address
