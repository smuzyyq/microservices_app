from passlib.context import CryptContext

from domain.entities import TokenPayload, User
from domain.exceptions import InvalidCredentialsError
from infrastructure.jwt_handler import IJWTHandler
from interfaces.repositories.user_repository import IUserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginUserUseCase:
    def __init__(self, user_repo: IUserRepository, jwt: IJWTHandler) -> None:
        self.user_repo = user_repo
        self.jwt = jwt

    def execute(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repo.find_by_email(email)
        if user is None or not pwd_context.verify(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password.")

        token = self.jwt.create_token(
            TokenPayload(
                user_id=user.id,
                email=user.email,
                role=user.role.value,
            )
        )
        return user, token
