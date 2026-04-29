from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    order_database_url: str
    auth_verify_url: str = "http://auth-service:8001/auth/verify"
    product_service_url: str = "http://product-service:8002/products"
    service_name: str = "order"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
