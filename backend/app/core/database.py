from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

from app.core.config import settings

# Determine dialect specific options
is_sqlite = "sqlite" in settings.DATABASE_URL

if is_sqlite:
    connect_args = {"check_same_thread": False}
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        connect_args=connect_args,
    )
else:
    # PostgreSQL / asyncpg connection pool configuration
    if settings.DB_POOL_SIZE <= 0:
        from sqlalchemy.pool import NullPool
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            poolclass=NullPool,
            pool_pre_ping=True,
        )
    else:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
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


async def dispose_db():
    """Dispose engine connection pool upon shutdown."""
    await engine.dispose()


import re


def sync_sqlite_columns(sync_conn):
    """Safely adds missing columns in SQLite without dropping or recreating tables."""
    # 1. users table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(users)")
    existing_user_cols = {row[1] for row in res.fetchall()}
    if "username" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN username VARCHAR(50)")
    if "is_suspended" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT 0")
    if "suspended_at" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN suspended_at DATETIME")
    if "suspended_by" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN suspended_by INTEGER")
    if "suspension_reason" not in existing_user_cols:
        sync_conn.exec_driver_sql("ALTER TABLE users ADD COLUMN suspension_reason TEXT")

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
    if "currency" not in existing_sp_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsor_profiles ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'")

    # 4. projects table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(projects)")
    existing_proj_cols = {row[1] for row in res.fetchall()}
    if "industry" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN industry VARCHAR(100)")
    if "problem_statement" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN problem_statement TEXT")
    if "proposed_solution" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN proposed_solution TEXT")
    if "target_market" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN target_market TEXT")
    if "value_proposition" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN value_proposition TEXT")
    if "current_progress" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN current_progress TEXT")
    if "funding_received" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN funding_received FLOAT DEFAULT 0.0")
    if "currency" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'")
    if "required_support" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN required_support JSON DEFAULT '[]'")
    if "required_resources" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN required_resources TEXT")
    if "skills_needed" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN skills_needed JSON DEFAULT '[]'")
    if "tech_stack" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN tech_stack JSON DEFAULT '[]'")
    if "website_url" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN website_url VARCHAR(512)")
    if "logo_url" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN logo_url VARCHAR(512)")
    if "video_url" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN video_url VARCHAR(512)")
    if "cover_image_url" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN cover_image_url VARCHAR(512)")
    if "location" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN location VARCHAR(255)")
    if "timeline" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN timeline VARCHAR(255)")
    if "moderation_status" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN moderation_status VARCHAR(50) DEFAULT 'approved'")
    if "moderation_reason" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN moderation_reason TEXT")
    if "moderated_at" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN moderated_at DATETIME")
    if "moderated_by" not in existing_proj_cols:
        sync_conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN moderated_by INTEGER")

    # 5. sponsorship_requests table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(sponsorship_requests)")
    existing_req_cols = {row[1] for row in res.fetchall()}
    if "currency" not in existing_req_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_requests ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'")
    if "requested_resources" not in existing_req_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_requests ADD COLUMN requested_resources TEXT")
    if "response_note" not in existing_req_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_requests ADD COLUMN response_note TEXT")

    # 6. sponsorship_commitments table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(sponsorship_commitments)")
    existing_comm_cols = {row[1] for row in res.fetchall()}
    if "title" not in existing_comm_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_commitments ADD COLUMN title VARCHAR(255)")
    if "description" not in existing_comm_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_commitments ADD COLUMN description TEXT")
    if "currency" not in existing_comm_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_commitments ADD COLUMN currency VARCHAR(10) DEFAULT 'INR'")
    if "follow_up_reason" not in existing_comm_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_commitments ADD COLUMN follow_up_reason VARCHAR(255)")
    if "cancellation_type" not in existing_comm_cols:
        sync_conn.exec_driver_sql("ALTER TABLE sponsorship_commitments ADD COLUMN cancellation_type VARCHAR(50)")

    # 7. commitment_updates table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(commitment_updates)")
    existing_upd_cols = {row[1] for row in res.fetchall()}
    if "update_type" not in existing_upd_cols:
        sync_conn.exec_driver_sql("ALTER TABLE commitment_updates ADD COLUMN update_type VARCHAR(50) DEFAULT 'status_change'")
    if "title" not in existing_upd_cols:
        sync_conn.exec_driver_sql("ALTER TABLE commitment_updates ADD COLUMN title VARCHAR(255)")
    if "cancellation_type" not in existing_upd_cols:
        sync_conn.exec_driver_sql("ALTER TABLE commitment_updates ADD COLUMN cancellation_type VARCHAR(50)")
    if "evidence_reference" not in existing_upd_cols:
        sync_conn.exec_driver_sql("ALTER TABLE commitment_updates ADD COLUMN evidence_reference VARCHAR(512)")
    if "event_date" not in existing_upd_cols:
        sync_conn.exec_driver_sql("ALTER TABLE commitment_updates ADD COLUMN event_date DATETIME")

    # 8. trust_scores table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(trust_scores)")
    existing_ts_cols = {row[1] for row in res.fetchall()}
    if "score_version" not in existing_ts_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_scores ADD COLUMN score_version INTEGER DEFAULT 1")
    if "completed_milestones_count" not in existing_ts_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_scores ADD COLUMN completed_milestones_count INTEGER DEFAULT 0")

    # 9. trust_score_events table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(trust_score_events)")
    existing_tse_cols = {row[1] for row in res.fetchall()}
    if "score_before" not in existing_tse_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_score_events ADD COLUMN score_before INTEGER")
    if "score_after" not in existing_tse_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_score_events ADD COLUMN score_after INTEGER")
    if "reference_id" not in existing_tse_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_score_events ADD COLUMN reference_id INTEGER")
    if "reference_type" not in existing_tse_cols:
        sync_conn.exec_driver_sql("ALTER TABLE trust_score_events ADD COLUMN reference_type VARCHAR(50)")

    # 10. messages table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(messages)")
    existing_msg_cols = {row[1] for row in res.fetchall()}
    if "conversation_id" not in existing_msg_cols:
        sync_conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE")
    if "read_at" not in existing_msg_cols:
        sync_conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN read_at DATETIME")

    # 11. notifications table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(notifications)")
    existing_notif_cols = {row[1] for row in res.fetchall()}
    if "entity_type" not in existing_notif_cols:
        sync_conn.exec_driver_sql("ALTER TABLE notifications ADD COLUMN entity_type VARCHAR(50)")
    if "entity_id" not in existing_notif_cols:
        sync_conn.exec_driver_sql("ALTER TABLE notifications ADD COLUMN entity_id INTEGER")
    if "read_at" not in existing_notif_cols:
        sync_conn.exec_driver_sql("ALTER TABLE notifications ADD COLUMN read_at DATETIME")

    # 12. reports table
    res = sync_conn.exec_driver_sql("PRAGMA table_info(reports)")
    existing_rep_cols = {row[1] for row in res.fetchall()}
    if "category" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN category VARCHAR(50) DEFAULT 'other'")
    if "reported_sponsorship_request_id" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN reported_sponsorship_request_id INTEGER")
    if "reported_commitment_id" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN reported_commitment_id INTEGER")
    if "reviewed_by" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN reviewed_by INTEGER")
    if "reviewed_at" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN reviewed_at DATETIME")
    if "resolution_note" not in existing_rep_cols:
        sync_conn.exec_driver_sql("ALTER TABLE reports ADD COLUMN resolution_note TEXT")


async def init_db():
    """Create database tables if they do not exist, and sync any new columns."""
    # Import all models to ensure they are registered on Base.metadata
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if is_sqlite:
            await conn.run_sync(sync_sqlite_columns)

