from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.trust import (
    TrustScoreRead,
    TrustScorePublicRead,
    TrustScoreHistoryResponse,
)
from app.services.trust_service import TrustService

router = APIRouter()


@router.get("/me", response_model=TrustScoreRead, summary="Get Current User Trust Score")
async def get_my_trust_score(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve explainable Trust Score, factor breakdown, and audit events for authenticated user."""
    return await TrustService.get_trust_breakdown(db, current_user.id)


@router.get("/history", response_model=TrustScoreHistoryResponse, summary="Get Trust Event History")
async def get_my_trust_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve paginated auditable history of trust score changes for authenticated user."""
    return await TrustService.get_trust_history(db, current_user.id, limit=limit, offset=offset)


@router.post("/recalculate", response_model=TrustScoreRead, summary="Recalculate Trust Score")
async def recalculate_my_trust_score(
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deterministically recalculate Trust Score from factual platform records and idempotent events."""
    target_id = current_user.id
    if user_id and user_id != current_user.id:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can recalculate other users' scores.")
        target_id = user_id

    await TrustService.recalculate_trust_score(db, target_id)
    return await TrustService.get_trust_breakdown(db, target_id)


@router.get("/users/{user_id}", response_model=TrustScorePublicRead, summary="Get Safe Public Trust Score")
async def get_public_user_trust_score(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve public Trust Score breakdown for any user. Strips private events and internal notes."""
    return await TrustService.get_public_trust_breakdown(db, user_id)


@router.get("/{user_id}", response_model=TrustScoreRead, summary="Get User Trust Score (Legacy/Compat)")
async def get_user_trust_score(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve Trust Score. Non-owners receive public-safe breakdown with private events omitted."""
    if user_id == current_user.id or current_user.role == UserRole.ADMIN:
        return await TrustService.get_trust_breakdown(db, user_id)

    public_data = await TrustService.get_public_trust_breakdown(db, user_id)
    return TrustScoreRead(
        id=public_data.id,
        user_id=public_data.user_id,
        score=public_data.score,
        verification_points=public_data.verification_points,
        commitments_points=public_data.commitments_points,
        responsiveness_points=public_data.responsiveness_points,
        activity_points=public_data.activity_points,
        completed_commitments_count=public_data.completed_commitments_count,
        cancelled_commitments_count=0,
        completed_milestones_count=public_data.completed_milestones_count,
        avg_response_hours=public_data.avg_response_hours,
        score_version=public_data.score_version,
        last_calculated_at=public_data.last_calculated_at,
        factors=public_data.factors,
        events=[],  # Private events omitted for other users
    )
