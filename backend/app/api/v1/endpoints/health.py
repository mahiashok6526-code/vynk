import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db, engine
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint validating API and database connectivity."""
    start_time = time.time()
    db_status = "healthy"
    error_msg = None

    try:
        # Ping the database
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "unhealthy"
        error_msg = str(exc)

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database": {
            "status": db_status,
            "dialect": engine.dialect.name,
            "latency_ms": latency_ms,
            "error": error_msg,
        }
    }
