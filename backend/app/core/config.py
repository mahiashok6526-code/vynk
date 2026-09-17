import os
from typing import List, Union, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "Vynk API"
    VERSION: str = "1.0.0"
    ENV: str = "development"
    ENVIRONMENT: Optional[str] = None
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "vynk_dev_secret_key_92837482910384759281740294857102938475"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    # Default to async SQLite for local development and unit tests
    DATABASE_URL: str = "sqlite+aiosqlite:///./vynk.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # AI Service Configuration
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @model_validator(mode="after")
    def validate_environment_and_production_settings(self) -> "Settings":
        # Synchronize ENV and ENVIRONMENT
        if self.ENVIRONMENT:
            self.ENV = self.ENVIRONMENT.lower()
        else:
            self.ENVIRONMENT = self.ENV.lower()

        is_production = self.ENV == "production"

        if is_production:
            # 1. Reject default/insecure/missing SECRET_KEY
            insecure_defaults = [
                "vynk_dev_secret",
                "secret",
                "dev-secret",
                "change-me",
                "password",
                "123456",
            ]
            if (
                not self.SECRET_KEY
                or len(self.SECRET_KEY.strip()) < 32
                or any(self.SECRET_KEY.lower().startswith(d) for d in insecure_defaults)
            ):
                raise ValueError(
                    "Insecure or missing SECRET_KEY in production environment. "
                    "A strong, randomly generated secret key (at least 32 characters) must be configured via SECRET_KEY environment variable."
                )

            # 2. Reject SQLite in production
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "SQLite database is not permitted in production. "
                    "Configure a production PostgreSQL database URL using asyncpg (e.g., postgresql+asyncpg://user:pass@host:5432/dbname)."
                )

            # 3. Reject wildcard CORS in production
            if "*" in self.BACKEND_CORS_ORIGINS:
                raise ValueError(
                    "Wildcard '*' CORS origins are not permitted in production with credentials. "
                    "Configure explicit frontend domain origins in BACKEND_CORS_ORIGINS."
                )

        return self


settings = Settings()
