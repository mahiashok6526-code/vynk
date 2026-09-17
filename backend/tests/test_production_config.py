import pytest
from httpx import AsyncClient
from app.core.config import Settings


def test_development_config_defaults():
    """Verify development mode accepts SQLite and local defaults."""
    dev_settings = Settings(
        ENV="development",
        DATABASE_URL="sqlite+aiosqlite:///./vynk.db",
        SECRET_KEY="vynk_dev_secret_key_92837482910384759281740294857102938475",
        BACKEND_CORS_ORIGINS=["http://localhost:5173"],
    )
    assert dev_settings.ENV == "development"
    assert dev_settings.DATABASE_URL.startswith("sqlite")
    assert not dev_settings.DEBUG


def test_production_config_valid():
    """Verify valid production settings with PostgreSQL and strong secret are accepted."""
    prod_settings = Settings(
        ENV="production",
        DATABASE_URL="postgresql+asyncpg://vynk_user:StrongPass123!@db.vynk.io:5432/vynk_prod",
        SECRET_KEY="a" * 32,  # 32 characters strong secret
        BACKEND_CORS_ORIGINS=["https://vynk.io", "https://app.vynk.io"],
    )
    assert prod_settings.ENV == "production"
    assert "postgresql+asyncpg" in prod_settings.DATABASE_URL
    assert len(prod_settings.BACKEND_CORS_ORIGINS) == 2


def test_production_rejects_insecure_secret():
    """Verify production fails safely if insecure or default SECRET_KEY is used."""
    with pytest.raises(ValueError, match="Insecure or missing SECRET_KEY in production"):
        Settings(
            ENV="production",
            DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
            SECRET_KEY="vynk_dev_secret_key_92837482910384759281740294857102938475",
            BACKEND_CORS_ORIGINS=["https://vynk.io"],
        )

    with pytest.raises(ValueError, match="Insecure or missing SECRET_KEY in production"):
        Settings(
            ENV="production",
            DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
            SECRET_KEY="short_secret",
            BACKEND_CORS_ORIGINS=["https://vynk.io"],
        )


def test_production_rejects_sqlite():
    """Verify production fails safely if SQLite is configured."""
    with pytest.raises(ValueError, match="SQLite database is not permitted in production"):
        Settings(
            ENV="production",
            DATABASE_URL="sqlite+aiosqlite:///./vynk.db",
            SECRET_KEY="a" * 32,
            BACKEND_CORS_ORIGINS=["https://vynk.io"],
        )


def test_production_rejects_wildcard_cors():
    """Verify production fails safely if wildcard '*' CORS is configured."""
    with pytest.raises(ValueError, match="Wildcard '\\*' CORS origins are not permitted in production"):
        Settings(
            ENV="production",
            DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db",
            SECRET_KEY="a" * 32,
            BACKEND_CORS_ORIGINS=["*"],
        )


@pytest.mark.asyncio
async def test_health_check_production_safety(client: AsyncClient):
    """Verify health endpoint responds with required telemetry and safe error format."""
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "database" in data
    assert "latency_ms" in data["database"]
    assert data["database"]["status"] == "healthy"
    # Ensure no credentials or passwords in response
    assert "password" not in res.text.lower()
    assert "secret" not in res.text.lower()


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Verify standard security headers are present on all responses."""
    res = await client.get("/api/v1/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_root_endpoint_metadata(client: AsyncClient):
    """Verify root API endpoint exposes platform metadata without leakage."""
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["app"] == "Vynk"
    assert "version" in data
    assert "health" in data
