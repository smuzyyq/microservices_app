from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from domain.entities import TokenPayload, User
from domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from infrastructure.database import get_db
from infrastructure.jwt_handler import IJWTHandler, JWTHandler
from interfaces.repositories.user_repository import IUserRepository, UserRepository
from interfaces.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenVerifyResponse,
    UserResponse,
)
from use_cases.login_user import LoginUserUseCase
from use_cases.register_user import RegisterUserUseCase
from use_cases.verify_token import VerifyTokenUseCase

router = APIRouter(tags=["auth"])


def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)


def get_jwt_handler() -> IJWTHandler:
    return JWTHandler()


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing.")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header.")
    return token


def _map_domain_exception(error: Exception) -> HTTPException:
    if isinstance(error, UserAlreadyExistsError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, InvalidCredentialsError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    if isinstance(error, UserNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, (TokenExpiredError, InvalidTokenError)):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected authentication error.")


def _to_auth_response(user: User, token: str) -> AuthResponse:
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        access_token=token,
    )


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


def get_current_payload(
    authorization: str | None = Header(default=None, alias="Authorization"),
    jwt_handler: IJWTHandler = Depends(get_jwt_handler),
) -> TokenPayload:
    token = _extract_bearer_token(authorization)
    use_case = VerifyTokenUseCase(jwt_handler)
    try:
        return use_case.execute(token)
    except (TokenExpiredError, InvalidTokenError) as exc:
        raise _map_domain_exception(exc) from exc


def get_current_user(
    payload: TokenPayload = Depends(get_current_payload),
    user_repo: IUserRepository = Depends(get_user_repository),
) -> User:
    user = user_repo.find_by_id(UUID(str(payload.user_id)))
    if user is None:
        raise _map_domain_exception(UserNotFoundError("User not found."))
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    user_repo: IUserRepository = Depends(get_user_repository),
    jwt_handler: IJWTHandler = Depends(get_jwt_handler),
) -> AuthResponse:
    use_case = RegisterUserUseCase(user_repo, jwt_handler)
    try:
        user, token = use_case.execute(payload.email, payload.password, payload.full_name)
    except UserAlreadyExistsError as exc:
        raise _map_domain_exception(exc) from exc
    return _to_auth_response(user, token)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    user_repo: IUserRepository = Depends(get_user_repository),
    jwt_handler: IJWTHandler = Depends(get_jwt_handler),
) -> AuthResponse:
    use_case = LoginUserUseCase(user_repo, jwt_handler)
    try:
        user, token = use_case.execute(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise _map_domain_exception(exc) from exc
    return _to_auth_response(user, token)


@router.get("/verify", response_model=TokenVerifyResponse)
def verify(payload: TokenPayload = Depends(get_current_payload)) -> TokenVerifyResponse:
    return TokenVerifyResponse(
        user_id=payload.user_id,
        email=payload.email,
        role=payload.role,
        valid=True,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _to_user_response(current_user)
