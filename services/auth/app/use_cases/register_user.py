from datetime import datetime
from uuid import uuid4

from passlib.context import CryptContext

from domain.entities import TokenPayload, User, UserRole
from domain.exceptions import UserAlreadyExistsError
from infrastructure.jwt_handler import IJWTHandler
from interfaces.repositories.user_repository import IUserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, jwt: IJWTHandler) -> None:
        self.user_repo = user_repo
        self.jwt = jwt

    def execute(self, email: str, password: str, full_name: str) -> tuple[User, str]:
        existing_user = self.user_repo.find_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(f"User with email '{email}' already exists.")

        user = User(
            id=uuid4(),
            email=email,
            hashed_password=pwd_context.hash(password),
            full_name=full_name,
            role=UserRole.customer,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        saved_user = self.user_repo.save(user)
        token = self.jwt.create_token(
            TokenPayload(
                user_id=saved_user.id,
                email=saved_user.email,
                role=saved_user.role.value,
            )
        )
        return saved_user, token
