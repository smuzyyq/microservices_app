from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    payment_database_url: str
    auth_verify_url: str = "http://auth-service:8001/auth/verify"
    service_name: str = "payment"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
