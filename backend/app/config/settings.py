"""Application settings loaded from environment variables."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """BloodTrace application settings."""

    # Application
    APP_NAME: str = "BloodTrace"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://bloodtrace:bloodtrace_secret@localhost:5432/bloodtrace"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "bloodtrace-dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3700"]

    # Webhooks
    WEBHOOK_URLS: List[str] = []
    WEBHOOK_SECRET: str = "webhook-secret-change-in-production"

    # Stock thresholds
    LOW_STOCK_THRESHOLD: int = 5
    EXPIRY_WARNING_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
