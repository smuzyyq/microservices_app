from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt

from config import settings
from domain.entities import TokenPayload
from domain.exceptions import InvalidTokenError, TokenExpiredError


class IJWTHandler(ABC):
    @abstractmethod
    def create_token(self, payload: TokenPayload) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayload:
        raise NotImplementedError


class JWTHandler(IJWTHandler):
    def create_token(self, payload: TokenPayload) -> str:
        expire_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        token_data = {
            "user_id": str(payload.user_id),
            "email": payload.email,
            "role": payload.role,
            "exp": expire_at,
        }
        return jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        try:
            data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired.") from exc
        except JWTError as exc:
            raise InvalidTokenError("Token is invalid.") from exc

        try:
            return TokenPayload(
                user_id=UUID(str(data["user_id"])),
                email=data["email"],
                role=data["role"],
            )
        except KeyError as exc:
            raise InvalidTokenError("Token payload is incomplete.") from exc
