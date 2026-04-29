from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    auth_database_url: str
    jwt_secret: str = "foodrush-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
