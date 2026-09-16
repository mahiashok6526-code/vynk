from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.sponsorship import SponsorshipCommitment
from app.models.trust import TrustScore
from app.models.moderation import VerificationRecord, Report

router = APIRouter()


@router.get("/stats", summary="Platform Statistics")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only summary of platform metrics and verification queues."""
    users_count = await db.scalar(select(func.count(User.id)))
    entrepreneurs_count = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.ENTREPRENEUR))
    sponsors_count = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.SPONSOR))
    projects_count = await db.scalar(select(func.count(Project.id)))
    commitments_count = await db.scalar(select(func.count(SponsorshipCommitment.id)))
    total_committed_funding = await db.scalar(select(func.sum(SponsorshipCommitment.amount))) or 0.0
    avg_trust_score = await db.scalar(select(func.avg(TrustScore.score))) or 50.0

    pending_verifications = await db.scalar(select(func.count(VerificationRecord.id)).where(VerificationRecord.status == "pending"))
    pending_reports = await db.scalar(select(func.count(Report.id)).where(Report.status == "pending"))

    return {
        "users": {
            "total": users_count,
            "entrepreneurs": entrepreneurs_count,
            "sponsors": sponsors_count,
        },
        "projects_count": projects_count,
        "commitments": {
            "total_count": commitments_count,
            "total_funding_usd": float(total_committed_funding),
        },
        "average_trust_score": round(float(avg_trust_score), 1),
        "queue": {
            "pending_verifications": pending_verifications,
            "pending_reports": pending_reports,
        }
    }
