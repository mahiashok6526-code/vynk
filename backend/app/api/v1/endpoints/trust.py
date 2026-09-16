from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.trust import TrustScoreRead
from app.services.trust_service import TrustService

router = APIRouter()


@router.get("/me", response_model=TrustScoreRead, summary="Get Current User Trust Score")
async def get_my_trust_score(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve explainable Trust Score and activity indicators for authenticated user."""
    return await TrustService.get_trust_breakdown(db, current_user.id)


@router.get("/{user_id}", response_model=TrustScoreRead, summary="Get User Trust Score")
async def get_user_trust_score(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve public Trust Score indicators for any platform user."""
    return await TrustService.get_trust_breakdown(db, user_id)
