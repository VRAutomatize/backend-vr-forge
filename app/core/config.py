"""Application configuration via environment variables."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "VRForge"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # Logging Configuration
    LOG_REQUEST_DETAILS: str = "standard"  # minimal, standard, verbose
    LOG_INVALID_REQUESTS: bool = True
    LOG_USER_AGENT: bool = True
    LOG_REFERER: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://vrforge:vrforge@localhost:5432/vrforge"

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = "vrforge-storage"
    AWS_S3_REGION: str = "us-east-1"

    # LLM Providers
    OPENAI_API_KEY: str = ""
    GOOGLE_GEMINI_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

