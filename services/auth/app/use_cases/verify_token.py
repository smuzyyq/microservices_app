from domain.entities import TokenPayload
from infrastructure.jwt_handler import IJWTHandler


class VerifyTokenUseCase:
    def __init__(self, jwt: IJWTHandler) -> None:
        self.jwt = jwt

    def execute(self, token: str) -> TokenPayload:
        return self.jwt.decode_token(token)
