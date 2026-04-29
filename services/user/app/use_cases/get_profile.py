from domain.entities import UserProfile
from domain.exceptions import ProfileNotFoundError
from interfaces.repositories.user_repository import IUserRepository


class GetProfileUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    def execute(self, user_id) -> UserProfile:
        profile = self.user_repo.get_profile(user_id)
        if profile is None:
            raise ProfileNotFoundError("Profile not found.")
        return profile
