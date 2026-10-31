"""
Central application configuration - all values loaded from environment.
Never hardcode secrets; use .env file for all sensitive values.
"""

from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application-wide settings sourced exclusively from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # don't crash on unrelated env vars
    )

    # -- Application --
    APP_NAME: str = "FinVault AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development | staging | production

    # -- Database --
    DATABASE_URL: str = (
        "postgresql+asyncpg://finvault:finvault123@localhost:5432/finvault_db"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False  # Set True to log all SQL queries

    # -- Redis --
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default cache lifetime

    # -- Auth / JWT --
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_USE_openssl_rand_hex_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # -- AI Providers --
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "openai"          # openai | anthropic
    AI_MODEL_OPENAI: str = "gpt-4o"
    AI_MODEL_ANTHROPIC: str = "claude-sonnet-4-20250514"
    AI_MAX_TOKENS: int = 2048
    AI_TEMPERATURE: float = 0.3          # Lower = more factual for finance

    # -- CORS --
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # -- Localisation --
    DEFAULT_CURRENCY: str = "INR"
    CURRENCY_SYMBOL: str = "\u20b9"      # Indian rupee sign
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"


@lru_cache()
def get_settings() -> Settings:
    """Return a module-level cached Settings instance (instantiated once)."""
    return Settings()


# Module-level singleton for import convenience
settings = get_settings()