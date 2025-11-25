from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field
import os


class Settings(BaseSettings):
    # 🌐 Project info
    PROJECT_NAME: str = "Ecommerce API"
    DATABASE_URL: str

    # 🔐 JWT & Auth config
    ACCESS_SECRET: str = Field("super-secret-access", description="JWT access token secret")
    REFRESH_SECRET: str = Field("super-secret-refresh", description="JWT refresh token secret")
    ACCESS_EXPIRE_MINUTES: int = Field(30, description="Access token expiry in minutes")
    REFRESH_EXPIRE_DAYS: int = Field(7, description="Refresh token expiry in days")

    # 🛡️ Environment & CORS
    ENV: str = Field("development", description="Environment mode (development or production)")
    BACKEND_CORS_ORIGINS: str | None = None

    class Config:
        # ================================
        # 🧠 Auto-detect env file
        # ================================
        env_file = (
            ".env.prod" if os.getenv("ENV") == "production" else ".env"
        )
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance (singleton)."""
    return Settings()


# Global settings instance
settings = get_settings()
