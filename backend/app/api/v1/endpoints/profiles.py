from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.schemas.profile import (
    ProfileUpdateRequest,
    ProfileCompletionRead,
    PublicProfileRead,
    ProjectSummary,
)
from app.services.profile_service import ProfileService

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Allows endpoints to optionally identify the caller if a valid token is present."""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        return None
    try:
        user_id = int(payload.get("sub"))
        return await AuthService.get_user_by_id(db, user_id)
    except Exception:
        return None


def serialize_public_profile(user: User, is_own_profile: bool = False) -> PublicProfileRead:
    """Formats a User model into the PublicProfileRead schema."""
    ep_data = None
    projects = []
    if user.role == UserRole.ENTREPRENEUR and user.entrepreneur_profile:
        ep = user.entrepreneur_profile
        ep_data = {
            "stage": ep.stage,
            "industry": ep.industry,
            "skills": ep.skills or [],
            "experience": ep.experience or [],
            "education": ep.education or [],
            "achievements": ep.achievements or [],
            "pitch_deck_url": ep.pitch_deck_url,
            "linkedin_url": ep.linkedin_url,
            "github_url": ep.github_url,
            "website_url": ep.website_url,
        }
        if ep.projects:
            projects = [
                ProjectSummary(
                    id=p.id,
                    title=p.title,
                    slug=p.slug,
                    tagline=p.tagline,
                    description=p.description,
                    category=p.category,
                    stage=p.stage.value if hasattr(p.stage, "value") else str(p.stage),
                    funding_goal=p.funding_goal,
                    current_funding=p.current_funding,
                    demo_url=p.demo_url,
                    pitch_deck_url=p.pitch_deck_url,
                    status=p.status.value if hasattr(p.status, "value") else str(p.status),
                    created_at=p.created_at,
                )
                for p in ep.projects
            ]

    sp_data = None
    if user.role == UserRole.SPONSOR and user.sponsor_profile:
        sp = user.sponsor_profile
        sp_data = {
            "organization_name": sp.organization_name,
            "logo_url": sp.logo_url,
            "about": sp.about,
            "industry": sp.industry,
            "sponsor_type": sp.sponsor_type,
            "focus_industries": sp.focus_industries or [],
            "min_budget": sp.min_budget,
            "max_budget": sp.max_budget,
            "preferred_sponsorship_types": sp.preferred_sponsorship_types or [],
            "sponsorship_interests": sp.sponsorship_interests or [],
            "areas_supported": sp.areas_supported or [],
            "previous_collaborations": sp.previous_collaborations or [],
        }

    trust_data = None
    if user.trust_score:
        ts = user.trust_score
        trust_data = {
            "score": ts.score,
            "verification_points": ts.verification_points,
            "commitments_points": ts.commitments_points,
            "responsiveness_points": ts.responsiveness_points,
            "activity_points": ts.activity_points,
            "completed_commitments_count": ts.completed_commitments_count,
        }

    completion = ProfileService.calculate_completion(user) if is_own_profile else None

    return PublicProfileRead(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        is_verified=user.is_verified,
        avatar_url=user.avatar_url,
        headline=user.headline,
        bio=user.bio,
        location=user.location,
        created_at=user.created_at,
        entrepreneur_profile=ep_data,
        sponsor_profile=sp_data,
        trust_score=trust_data,
        projects=projects,
        completion=completion,
        is_own_profile=is_own_profile,
    )


@router.get("/me", response_model=PublicProfileRead, summary="Get Current Authenticated Profile")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the full profile, completion metrics, and role details for the logged-in user."""
    # Re-fetch user with all nested relationships
    user = await ProfileService.get_user_by_identifier(db, str(current_user.id))
    if not user:
        user = current_user
    return serialize_public_profile(user, is_own_profile=True)


@router.put("/me", response_model=PublicProfileRead, summary="Update Current Authenticated Profile")
async def update_my_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile fields with validation and uniqueness checks."""
    user = await ProfileService.get_user_by_identifier(db, str(current_user.id))
    if not user:
        user = current_user

    updated_user = await ProfileService.update_profile(db, user, update_data)
    # Refresh to return full updated object
    refreshed = await ProfileService.get_user_by_identifier(db, str(updated_user.id))
    return serialize_public_profile(refreshed or updated_user, is_own_profile=True)


@router.get("/completion/me", response_model=ProfileCompletionRead, summary="Get Profile Completion Metrics")
async def get_my_completion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate profile completion percentage and missing fields for the active user."""
    user = await ProfileService.get_user_by_identifier(db, str(current_user.id))
    return ProfileService.calculate_completion(user or current_user)


@router.get("/{identifier}", response_model=PublicProfileRead, summary="Get Public Profile by Username or ID")
async def get_public_profile(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    optional_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve public profile for an Entrepreneur or Sponsor by @username or user ID."""
    user = await ProfileService.get_user_by_identifier(db, identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with identifier '{identifier}' was not found.",
        )

    is_own = bool(optional_user and optional_user.id == user.id)
    return serialize_public_profile(user, is_own_profile=is_own)
