from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

from app.core.config import settings

# Determine dialect specific options
is_sqlite = "sqlite" in settings.DATABASE_URL
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

# Enable foreign keys for SQLite
if is_sqlite:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


import re


def sync_sqlite_columns(sync_conn):
    """Safely adds missing columns in SQLite without dropping or recreating tables."""
    # 1. users table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(users)")
    existing_user_cols = {row[1] for row in res.fetchall()}
    if "username" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN username VARCHAR(50)")

    # Backfill username for any existing users with NULL or empty username
    res = sync_conn.exec_driver_sql("SELECT id, email, full_name FROM users WHERE username IS NULL OR username = ''")
    users_to_backfill = res.fetchall()
    for u_id, u_email, u_name in users_to_backfill:
        base_name = u_email.split('@')[0] if u_email else f"user_{u_id}"
        clean_base = re.sub(r'[^a-zA-Z0-9_]', '_', base_name).lower()
        if len(clean_base) < 3:
            clean_base = f"{clean_base}_{u_id}"
        candidate = clean_base[:30]

        check_res = sync_conn.exec_driver_sql("SELECT id FROM users WHERE username = :uname AND id != :uid", {"uname": candidate, "uid": u_id})
        if check_res.fetchone():
            candidate = f"{candidate[:24]}_{u_id}"
        sync_conn.exec_driver_sql("UPDATE users SET username = :uname WHERE id = :uid", {"uname": candidate, "uid": u_id})

    # 2. entrepreneur_profiles table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(entrepreneur_profiles)")
    existing_ep_cols = {row[1] for row in res.fetchall()}
    if "experience" not in existing_ep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE entrepreneur_profiles ADD COLUMN experience JSON DEFAULT '[]'")
    if "education" not in existing_ep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE entrepreneur_profiles ADD COLUMN education JSON DEFAULT '[]'")
    if "achievements" not in existing_ep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE entrepreneur_profiles ADD COLUMN achievements JSON DEFAULT '[]'")

    # 3. sponsor_profiles table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(sponsor_profiles)")
    existing_sp_cols = {row[1] for row in res.fetchall()}
    if "logo_url" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN logo_url VARCHAR(512)")
    if "about" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN about TEXT")
    if "industry" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN industry VARCHAR(100)")
    if "sponsorship_interests" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN sponsorship_interests JSON DEFAULT '[]'")
    if "areas_supported" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN areas_supported JSON DEFAULT '[]'")
    if "previous_collaborations" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN previous_collaborations JSON DEFAULT '[]'")


async def init_db():
    """Create database tables if they do not exist, and sync any new columns."""
    # Import all models to ensure they are registered on Base.metadata
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if is_sqlite:
            await conn.run_sync(sync_sqlite_columns)

