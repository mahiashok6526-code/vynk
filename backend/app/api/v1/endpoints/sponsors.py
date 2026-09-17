import math
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User, UserRole, SponsorProfile
from app.models.trust import TrustScore
from app.schemas.sponsor import SponsorDiscoveryItem, SponsorPaginationResponse

router = APIRouter()


def format_sponsor_response(sp: SponsorProfile) -> SponsorDiscoveryItem:
    u = sp.user
    ts_score = u.trust_score.score if getattr(u, "trust_score", None) else 50

    return SponsorDiscoveryItem(
        id=sp.id,
        user_id=u.id,
        full_name=u.full_name,
        username=u.username,
        organization_name=sp.organization_name,
        logo_url=sp.logo_url,
        avatar_url=u.avatar_url,
        headline=u.headline,
        about=sp.about or u.bio,
        industry=sp.industry,
        sponsor_type=sp.sponsor_type or "individual_angel",
        focus_industries=sp.focus_industries or [],
        min_budget=sp.min_budget or 1000,
        max_budget=sp.max_budget or 50000,
        currency=getattr(sp, "currency", "INR") or "INR",
        preferred_sponsorship_types=sp.preferred_sponsorship_types or [],
        sponsorship_interests=sp.sponsorship_interests or [],
        areas_supported=sp.areas_supported or [],
        previous_collaborations=sp.previous_collaborations or [],
        location=u.location,
        is_verified=u.is_verified,
        trust_score=ts_score,
        created_at=sp.created_at,
    )


@router.get("/", response_model=Union[SponsorPaginationResponse, List[SponsorDiscoveryItem]])
async def list_sponsors(
    search: Optional[str] = Query(None),
    sponsor_type: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    sponsorship_type: Optional[str] = Query(None),
    min_budget: Optional[int] = Query(None),
    max_budget: Optional[int] = Query(None),
    is_verified: Optional[bool] = Query(None),
    location: Optional[str] = Query(None),
    sort: Optional[str] = Query("recent"),
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Discover active sponsors and funding partners on Vynk.
    Enforces privacy by design: private fields like email and password are never exposed.
    Supports database-level filtering, search, sorting and pagination.
    """
    base_conditions = [
        User.is_active == True,
        User.role == UserRole.SPONSOR,
    ]

    if search:
        search_pattern = f"%{search}%"
        base_conditions.append(
            User.full_name.ilike(search_pattern)
            | SponsorProfile.organization_name.ilike(search_pattern)
            | User.headline.ilike(search_pattern)
            | SponsorProfile.about.ilike(search_pattern)
            | SponsorProfile.industry.ilike(search_pattern)
        )

    if sponsor_type:
        base_conditions.append(SponsorProfile.sponsor_type.ilike(f"%{sponsor_type}%"))

    if industry:
        base_conditions.append(
            SponsorProfile.industry.ilike(f"%{industry}%")
            | cast(SponsorProfile.focus_industries, String).ilike(f"%{industry}%")
        )

    if sponsorship_type:
        base_conditions.append(
            cast(SponsorProfile.preferred_sponsorship_types, String).ilike(f"%{sponsorship_type}%")
            | cast(SponsorProfile.areas_supported, String).ilike(f"%{sponsorship_type}%")
        )

    if min_budget is not None:
        base_conditions.append(SponsorProfile.max_budget >= min_budget)

    if max_budget is not None:
        base_conditions.append(SponsorProfile.min_budget <= max_budget)

    if is_verified is not None:
        base_conditions.append(User.is_verified == is_verified)

    if location:
        base_conditions.append(User.location.ilike(f"%{location}%"))

    # Database-level count query for pagination
    count_query = (
        select(func.count(SponsorProfile.id))
        .join(User, SponsorProfile.user_id == User.id)
        .where(*base_conditions)
    )
    count_res = await db.execute(count_query)
    total_count = count_res.scalar() or 0

    # Sorting
    order_clauses = []
    if sort == "budget_high":
        order_clauses.append(SponsorProfile.max_budget.desc())
    elif sort == "budget_low":
        order_clauses.append(SponsorProfile.min_budget.asc())
    elif sort == "trust":
        # Join with TrustScore for ordering
        order_clauses.append(TrustScore.score.desc())
    elif sort == "name":
        order_clauses.append(User.full_name.asc())
    else:  # "recent"
        order_clauses.append(SponsorProfile.created_at.desc())

    query = (
        select(SponsorProfile)
        .join(User, SponsorProfile.user_id == User.id)
        .outerjoin(TrustScore, User.id == TrustScore.user_id)
        .where(*base_conditions)
        .options(
            selectinload(SponsorProfile.user).selectinload(User.trust_score),
        )
        .order_by(*order_clauses)
    )

    if page is not None:
        eff_offset = (page - 1) * limit
        query = query.offset(eff_offset).limit(limit)
    else:
        query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    sponsors = result.scalars().all()
    formatted = [format_sponsor_response(sp) for sp in sponsors]

    if page is not None:
        total_pages = math.ceil(total_count / limit) if limit > 0 else 1
        return SponsorPaginationResponse(
            results=formatted,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    return formatted


@router.get("/{id_or_username}", response_model=SponsorDiscoveryItem)
async def get_sponsor(
    id_or_username: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve public sponsor profile safely without exposing credentials or private information."""
    query = (
        select(SponsorProfile)
        .join(User, SponsorProfile.user_id == User.id)
        .options(
            selectinload(SponsorProfile.user).selectinload(User.trust_score),
        )
    )

    if id_or_username.isdigit():
        query = query.where(
            (SponsorProfile.id == int(id_or_username)) | (SponsorProfile.user_id == int(id_or_username))
        )
    else:
        clean_uname = id_or_username.lstrip("@").lower()
        query = query.where(User.username.ilike(clean_uname))

    result = await db.execute(query)
    sponsor = result.scalar_one_or_none()

    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsor profile not found.",
        )

    return format_sponsor_response(sponsor)
