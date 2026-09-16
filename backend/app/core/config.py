from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "Vynk API"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = "vynk_dev_secret_key_92837482910384759281740294857102938475"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    # Default to async SQLite for Phase 1 local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./vynk.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

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

    # AI Service Configuration (Pluggable for Phase 2)
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""


settings = Settings()
