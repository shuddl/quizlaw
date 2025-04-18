from typing import Dict, Any, Optional
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    These settings are loaded from environment variables and/or .env file.
    """

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # JWT Auth
    FLASK_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Stripe (for Premium subscriptions)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    PREMIUM_PRICE_ID: Optional[str] = None
    SUCCESS_URL: str = "http://localhost:5173/payment/success"
    CANCEL_URL: str = "http://localhost:5173/payment/cancel"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Scraper settings
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    SCRAPER_REQUEST_TIMEOUT: int = 30

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate and normalize DATABASE_URL."""
        # Ensure postgres:// becomes postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global instance
settings = Settings()