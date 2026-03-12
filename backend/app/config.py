"""Centralized configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///app.db"

    # Auth
    secret_key: str = "change-me-to-a-random-secret"
    access_token_expire_minutes: int = 60

    # OpenAI
    openai_api_key: str = ""

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:8000"]

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
