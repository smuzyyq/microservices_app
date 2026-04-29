from uuid import uuid4

from domain.entities import UserProfile
from interfaces.repositories.user_repository import IUserRepository


class UpdateProfileUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id, phone: str | None, avatar_url: str | None, default_address: str | None) -> UserProfile:
        profile = self.user_repo.get_profile(user_id)
        if profile is None:
            profile = UserProfile(
                id=uuid4(),
                user_id=user_id,
                phone=phone,
                avatar_url=avatar_url,
                default_address=default_address,
            )
        else:
            profile.phone = phone
            profile.avatar_url = avatar_url
            profile.default_address = default_address
        return self.user_repo.save_profile(profile)
