from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_entrepreneur, require_sponsor
from app.models.user import User, UserRole, SponsorProfile, EntrepreneurProfile
from app.models.project import Project, ProjectStatus
from app.models.ai_match import AIMatchExplanation
from app.schemas.ai_match import (
    ProjectMatchItem,
    SponsorMatchItem,
    MatchExplanationResponse,
    FactorScoreDetail,
)
from app.services.ai.compatibility_engine import CompatibilityEngine
from app.services.ai.gemini_provider import GeminiAIService
from app.core.config import settings

router = APIRouter()
engine = CompatibilityEngine()
gemini_service = GeminiAIService()


class MatchRequest(BaseModel):
    project_id: int


class MatchExplanationRequest(BaseModel):
    project_id: int
    sponsor_id: int


@router.get("/status", summary="Check AI Service Layer Status")
async def get_ai_status():
    """Returns AI service layer configuration and readiness for Phase 5 integration."""
    return {
        "status": "ready",
        "provider": settings.AI_PROVIDER,
        "gemini_ready": gemini_service.is_configured,
        "mode": "deterministic_compatibility_v1",
        "phase": 5,
        "notes": "Pluggable service architecture active with deterministic scoring and Google Gemini explanations.",
    }


# =============================================================================
# PHASE 5: SPONSOR -> PROJECTS RECOMMENDATIONS
# =============================================================================

@router.get(
    "/matches/projects",
    response_model=List[ProjectMatchItem],
    summary="Get AI Recommended Projects for Active Sponsor",
)
async def get_recommended_projects_for_sponsor(
    limit: int = Query(10, ge=1, le=50),
    min_score: int = Query(0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_sponsor),
):
    """Computes explainable, deterministic compatibility scores between the sponsor's

    investment criteria and all active published projects.
    """
    if not current_user.sponsor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsor profile not initialized.",
        )

    sp = current_user.sponsor_profile
    sponsor_dict = {
        "id": sp.id,
        "organization_name": sp.organization_name,
        "full_name": current_user.full_name,
        "sponsor_type": sp.sponsor_type or "angel",
        "industry": sp.industry or "",
        "focus_industries": sp.focus_industries or [],
        "min_budget": sp.min_budget or 1000,
        "max_budget": sp.max_budget or 1000000,
        "preferred_sponsorship_types": sp.preferred_sponsorship_types or [],
        "areas_supported": sp.areas_supported or [],
        "sponsorship_interests": sp.sponsorship_interests or [],
        "location": current_user.location or "",
    }

    # Fetch all publicly discoverable projects
    public_statuses = [
        ProjectStatus.PUBLISHED,
        ProjectStatus.SEEKING_SPONSORSHIP,
        ProjectStatus.IN_DISCUSSION,
        ProjectStatus.FUNDED,
        ProjectStatus.ACTIVE,
    ]
    query = (
        select(Project)
        .where(Project.status.in_(public_statuses))
        .options(
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
        )
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    candidates: List[ProjectMatchItem] = []
    for p in projects:
        p_dict = {
            "id": p.id,
            "title": p.title,
            "tagline": p.tagline,
            "category": p.category,
            "industry": p.industry or "",
            "stage": p.stage.value if hasattr(p.stage, "value") else str(p.stage),
            "funding_goal": p.funding_goal,
            "required_support": p.required_support or [],
            "tech_stack": p.tech_stack or [],
            "skills_needed": p.skills_needed or [],
            "location": p.location or "",
        }

        analysis = engine.evaluate_compatibility(p_dict, sponsor_dict)
        score = analysis["overall_score"]
        if score < min_score:
            continue

        # Extract founder and trust info
        founder_user = p.entrepreneur.user if (p.entrepreneur and p.entrepreneur.user) else None
        founder_name = founder_user.full_name if founder_user else "Entrepreneur"
        founder_username = founder_user.username if founder_user else None
        trust_score = founder_user.trust_score.score if (founder_user and founder_user.trust_score) else 50
        is_verified = founder_user.is_verified if founder_user else False

        factors_converted = {
            k: FactorScoreDetail(**v) for k, v in analysis["factors"].items()
        }

        candidates.append(
            ProjectMatchItem(
                project_id=p.id,
                title=p.title,
                tagline=p.tagline,
                category=p.category,
                industry=p.industry,
                stage=p_dict["stage"],
                funding_goal=p.funding_goal,
                current_funding=p.current_funding or 0.0,
                currency=p.currency or "INR",
                required_support=p.required_support or [],
                location=p.location,
                logo_url=p.logo_url,
                founder_name=founder_name,
                founder_username=founder_username,
                trust_score=trust_score,
                is_verified=is_verified,
                compatibility_score=score,
                factors=factors_converted,
                reasons=analysis["reasons"],
                mismatches=analysis["mismatches"],
                summary=analysis["summary"],
            )
        )

    # Sort by compatibility score descending (tie-breaker: project_id descending)
    candidates.sort(key=lambda x: (x.compatibility_score, x.project_id), reverse=True)
    return candidates[:limit]


# =============================================================================
# PHASE 5: ENTREPRENEUR -> SPONSORS RECOMMENDATIONS
# =============================================================================

@router.get(
    "/matches/sponsors",
    response_model=List[SponsorMatchItem],
    summary="Get AI Recommended Sponsors for Active Entrepreneur",
)
async def get_recommended_sponsors_for_entrepreneur(
    project_id: Optional[int] = Query(None, description="Target project ID. If omitted, uses entrepreneur's primary project."),
    limit: int = Query(10, ge=1, le=50),
    min_score: int = Query(0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Computes explainable, deterministic compatibility scores between an entrepreneur's

    project and active platform sponsors.
    """
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    ent_id = current_user.entrepreneur_profile.id

    # Resolve target project
    if project_id:
        p_q = select(Project).where(Project.id == project_id, Project.entrepreneur_id == ent_id)
        p_res = await db.execute(p_q)
        project = p_res.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or not owned by current user.",
            )
    else:
        # Default to latest published or draft project
        p_q = (
            select(Project)
            .where(Project.entrepreneur_id == ent_id)
            .order_by(Project.created_at.desc())
            .limit(1)
        )
        p_res = await db.execute(p_q)
        project = p_res.scalar_one_or_none()
        if not project:
            return []  # No projects created yet, cannot match sponsors

    p_dict = {
        "id": project.id,
        "title": project.title,
        "tagline": project.tagline,
        "category": project.category,
        "industry": project.industry or "",
        "stage": project.stage.value if hasattr(project.stage, "value") else str(project.stage),
        "funding_goal": project.funding_goal,
        "required_support": project.required_support or [],
        "tech_stack": project.tech_stack or [],
        "skills_needed": project.skills_needed or [],
        "location": project.location or "",
    }

    # Fetch active sponsors
    s_query = (
        select(SponsorProfile)
        .join(User, SponsorProfile.user_id == User.id)
        .where(User.is_active == True, User.role == UserRole.SPONSOR)
        .options(
            selectinload(SponsorProfile.user).selectinload(User.trust_score),
        )
    )
    s_res = await db.execute(s_query)
    sponsors = s_res.scalars().all()

    candidates: List[SponsorMatchItem] = []
    for sp in sponsors:
        u = sp.user
        if not u:
            continue

        s_dict = {
            "id": sp.id,
            "organization_name": sp.organization_name,
            "full_name": u.full_name,
            "sponsor_type": sp.sponsor_type or "angel",
            "industry": sp.industry or "",
            "focus_industries": sp.focus_industries or [],
            "min_budget": sp.min_budget or 1000,
            "max_budget": sp.max_budget or 1000000,
            "preferred_sponsorship_types": sp.preferred_sponsorship_types or [],
            "areas_supported": sp.areas_supported or [],
            "sponsorship_interests": sp.sponsorship_interests or [],
            "location": u.location or "",
        }

        analysis = engine.evaluate_compatibility(p_dict, s_dict)
        score = analysis["overall_score"]
        if score < min_score:
            continue

        ts_score = u.trust_score.score if u.trust_score else 50
        factors_converted = {
            k: FactorScoreDetail(**v) for k, v in analysis["factors"].items()
        }

        candidates.append(
            SponsorMatchItem(
                sponsor_id=sp.id,
                user_id=u.id,
                full_name=u.full_name,
                username=u.username,
                organization_name=sp.organization_name,
                sponsor_type=sp.sponsor_type or "angel",
                logo_url=sp.logo_url,
                avatar_url=u.avatar_url,
                headline=u.headline,
                focus_industries=sp.focus_industries or [],
                preferred_sponsorship_types=sp.preferred_sponsorship_types or [],
                areas_supported=sp.areas_supported or [],
                min_budget=sp.min_budget or 1000,
                max_budget=sp.max_budget or 100000,
                currency=sp.currency or "INR",
                location=u.location,
                trust_score=ts_score,
                is_verified=u.is_verified,
                compatibility_score=score,
                factors=factors_converted,
                reasons=analysis["reasons"],
                mismatches=analysis["mismatches"],
                summary=analysis["summary"],
            )
        )

    candidates.sort(key=lambda x: (x.compatibility_score, x.sponsor_id), reverse=True)
    return candidates[:limit]


# =============================================================================
# PHASE 5: ON-DEMAND EXPLANATION ENDPOINTS WITH CACHING
# =============================================================================

@router.get(
    "/matches/projects/{project_id}/explanation",
    response_model=MatchExplanationResponse,
    summary="Get Detailed Factor Breakdown and AI Explanation for Project Match",
)
async def get_project_match_explanation(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_sponsor),
):
    """Retrieves or generates on-demand Gemini AI explanation for a sponsor and project match."""
    if not current_user.sponsor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsor profile not initialized.",
        )

    sp = current_user.sponsor_profile

    # Fetch project
    p_q = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
        )
    )
    p_res = await db.execute(p_q)
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    founder_user = project.entrepreneur.user if (project.entrepreneur and project.entrepreneur.user) else None
    founder_trust_score = founder_user.trust_score.score if (founder_user and founder_user.trust_score) else 50

    # 1. Check existing cached explanation in database
    cache_q = select(AIMatchExplanation).where(
        AIMatchExplanation.project_id == project.id,
        AIMatchExplanation.sponsor_id == sp.id,
    )
    cache_res = await db.execute(cache_q)
    cached = cache_res.scalar_one_or_none()

    if cached:
        factors_converted = {k: FactorScoreDetail(**v) for k, v in cached.factors.items()}
        return MatchExplanationResponse(
            project_id=project.id,
            sponsor_id=sp.id,
            project_title=project.title,
            sponsor_name=sp.organization_name or current_user.full_name,
            compatibility_score=cached.compatibility_score,
            trust_score=founder_trust_score,
            factors=factors_converted,
            reasons=cached.reasons or [],
            mismatches=cached.mismatches or [],
            explanation=cached.explanation,
            ai_generated=cached.ai_generated,
            provider=cached.provider,
            model=cached.model,
            generated_at=cached.updated_at or cached.created_at,
        )

    # 2. Compute compatibility and generate grounded explanation
    p_dict = {
        "id": project.id,
        "title": project.title,
        "category": project.category,
        "industry": project.industry or "",
        "stage": project.stage.value if hasattr(project.stage, "value") else str(project.stage),
        "funding_goal": project.funding_goal,
        "required_support": project.required_support or [],
        "tech_stack": project.tech_stack or [],
        "skills_needed": project.skills_needed or [],
        "location": project.location or "",
    }
    s_dict = {
        "id": sp.id,
        "organization_name": sp.organization_name,
        "full_name": current_user.full_name,
        "sponsor_type": sp.sponsor_type or "angel",
        "industry": sp.industry or "",
        "focus_industries": sp.focus_industries or [],
        "min_budget": sp.min_budget or 1000,
        "max_budget": sp.max_budget or 1000000,
        "preferred_sponsorship_types": sp.preferred_sponsorship_types or [],
        "areas_supported": sp.areas_supported or [],
        "sponsorship_interests": sp.sponsorship_interests or [],
        "location": current_user.location or "",
    }

    analysis = await gemini_service.explain_match_compatibility(p_dict, s_dict)
    factors_raw = analysis["factors"]

    # 3. Cache result in database
    new_cache = AIMatchExplanation(
        project_id=project.id,
        sponsor_id=sp.id,
        compatibility_score=analysis["overall_score"],
        factors=factors_raw,
        reasons=analysis["reasons"],
        mismatches=analysis["mismatches"],
        explanation=analysis["explanation"],
        ai_generated=analysis["ai_generated"],
        provider=analysis["provider"],
        model=analysis["model"],
    )
    db.add(new_cache)
    await db.commit()
    await db.refresh(new_cache)

    factors_converted = {k: FactorScoreDetail(**v) for k, v in factors_raw.items()}
    return MatchExplanationResponse(
        project_id=project.id,
        sponsor_id=sp.id,
        project_title=project.title,
        sponsor_name=sp.organization_name or current_user.full_name,
        compatibility_score=new_cache.compatibility_score,
        trust_score=founder_trust_score,
        factors=factors_converted,
        reasons=new_cache.reasons,
        mismatches=new_cache.mismatches,
        explanation=new_cache.explanation,
        ai_generated=new_cache.ai_generated,
        provider=new_cache.provider,
        model=new_cache.model,
        generated_at=new_cache.created_at,
    )


@router.get(
    "/matches/sponsors/{sponsor_id}/explanation",
    response_model=MatchExplanationResponse,
    summary="Get Detailed Factor Breakdown and AI Explanation for Sponsor Match",
)
async def get_sponsor_match_explanation(
    sponsor_id: int,
    project_id: Optional[int] = Query(None, description="Project ID to evaluate. Defaults to entrepreneur's latest project."),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Retrieves or generates on-demand Gemini AI explanation for an entrepreneur and sponsor match."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    ent_id = current_user.entrepreneur_profile.id

    # Resolve project
    if project_id:
        p_q = select(Project).where(Project.id == project_id, Project.entrepreneur_id == ent_id)
        p_res = await db.execute(p_q)
        project = p_res.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    else:
        p_q = (
            select(Project)
            .where(Project.entrepreneur_id == ent_id)
            .order_by(Project.created_at.desc())
            .limit(1)
        )
        p_res = await db.execute(p_q)
        project = p_res.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No projects found for entrepreneur.")

    # Fetch sponsor profile
    s_q = (
        select(SponsorProfile)
        .where((SponsorProfile.id == sponsor_id) | (SponsorProfile.user_id == sponsor_id))
        .options(
            selectinload(SponsorProfile.user).selectinload(User.trust_score),
        )
    )
    s_res = await db.execute(s_q)
    sp = s_res.scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found.")

    u = sp.user
    sponsor_trust_score = u.trust_score.score if (u and u.trust_score) else 50

    # 1. Check cache
    cache_q = select(AIMatchExplanation).where(
        AIMatchExplanation.project_id == project.id,
        AIMatchExplanation.sponsor_id == sp.id,
    )
    cache_res = await db.execute(cache_q)
    cached = cache_res.scalar_one_or_none()

    if cached:
        factors_converted = {k: FactorScoreDetail(**v) for k, v in cached.factors.items()}
        return MatchExplanationResponse(
            project_id=project.id,
            sponsor_id=sp.id,
            project_title=project.title,
            sponsor_name=sp.organization_name or (u.full_name if u else "Sponsor"),
            compatibility_score=cached.compatibility_score,
            trust_score=sponsor_trust_score,
            factors=factors_converted,
            reasons=cached.reasons or [],
            mismatches=cached.mismatches or [],
            explanation=cached.explanation,
            ai_generated=cached.ai_generated,
            provider=cached.provider,
            model=cached.model,
            generated_at=cached.updated_at or cached.created_at,
        )

    # 2. Compute compatibility and generate explanation
    p_dict = {
        "id": project.id,
        "title": project.title,
        "category": project.category,
        "industry": project.industry or "",
        "stage": project.stage.value if hasattr(project.stage, "value") else str(project.stage),
        "funding_goal": project.funding_goal,
        "required_support": project.required_support or [],
        "tech_stack": project.tech_stack or [],
        "skills_needed": project.skills_needed or [],
        "location": project.location or "",
    }
    s_dict = {
        "id": sp.id,
        "organization_name": sp.organization_name,
        "full_name": u.full_name if u else "Sponsor",
        "sponsor_type": sp.sponsor_type or "angel",
        "industry": sp.industry or "",
        "focus_industries": sp.focus_industries or [],
        "min_budget": sp.min_budget or 1000,
        "max_budget": sp.max_budget or 1000000,
        "preferred_sponsorship_types": sp.preferred_sponsorship_types or [],
        "areas_supported": sp.areas_supported or [],
        "sponsorship_interests": sp.sponsorship_interests or [],
        "location": u.location if u else "",
    }

    analysis = await gemini_service.explain_match_compatibility(p_dict, s_dict)
    factors_raw = analysis["factors"]

    # 3. Cache in database
    new_cache = AIMatchExplanation(
        project_id=project.id,
        sponsor_id=sp.id,
        compatibility_score=analysis["overall_score"],
        factors=factors_raw,
        reasons=analysis["reasons"],
        mismatches=analysis["mismatches"],
        explanation=analysis["explanation"],
        ai_generated=analysis["ai_generated"],
        provider=analysis["provider"],
        model=analysis["model"],
    )
    db.add(new_cache)
    await db.commit()
    await db.refresh(new_cache)

    factors_converted = {k: FactorScoreDetail(**v) for k, v in factors_raw.items()}
    return MatchExplanationResponse(
        project_id=project.id,
        sponsor_id=sp.id,
        project_title=project.title,
        sponsor_name=sp.organization_name or (u.full_name if u else "Sponsor"),
        compatibility_score=new_cache.compatibility_score,
        trust_score=sponsor_trust_score,
        factors=factors_converted,
        reasons=new_cache.reasons,
        mismatches=new_cache.mismatches,
        explanation=new_cache.explanation,
        ai_generated=new_cache.ai_generated,
        provider=new_cache.provider,
        model=new_cache.model,
        generated_at=new_cache.created_at,
    )


# =============================================================================
# PHASE 1 BACKWARD COMPATIBILITY
# =============================================================================

@router.post("/match", summary="Get Explainable Matches for Project (Legacy)")
async def match_project_with_sponsors_legacy(
    data: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute compatibility rankings between a project and available sponsors."""
    project_q = select(Project).where(Project.id == data.project_id)
    project_res = await db.execute(project_q)
    project = project_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    sponsors_q = select(SponsorProfile).limit(20)
    sponsors_res = await db.execute(sponsors_q)
    sponsors = sponsors_res.scalars().all()

    project_dict = {
        "id": project.id,
        "title": project.title,
        "category": project.category,
        "stage": project.stage.value if hasattr(project.stage, "value") else str(project.stage),
        "funding_goal": project.funding_goal,
    }

    sponsors_list = [
        {
            "id": s.id,
            "organization_name": s.organization_name,
            "focus_industries": s.focus_industries or [],
            "min_budget": s.min_budget,
            "max_budget": s.max_budget,
            "preferred_sponsorship_types": s.preferred_sponsorship_types or [],
        }
        for s in sponsors
    ]

    matches = await engine.match_entrepreneur_and_sponsors(project_dict, sponsors_list)
    return {
        "project_id": project.id,
        "matches_count": len(matches),
        "matches": matches,
    }


@router.post("/explain", summary="Explain Match Factors (Legacy)")
async def explain_match_legacy(
    data: MatchExplanationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Provides a transparent breakdown of matching factors between project and sponsor."""
    project_q = select(Project).where(Project.id == data.project_id)
    project_res = await db.execute(project_q)
    project = project_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    sponsor_q = select(SponsorProfile).where(SponsorProfile.id == data.sponsor_id)
    sponsor_res = await db.execute(sponsor_q)
    sponsor = sponsor_res.scalar_one_or_none()
    if not sponsor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found.")

    project_dict = {
        "title": project.title,
        "category": project.category,
        "stage": project.stage.value if hasattr(project.stage, "value") else str(project.stage),
        "funding_goal": project.funding_goal,
    }
    sponsor_dict = {
        "organization_name": sponsor.organization_name,
        "focus_industries": sponsor.focus_industries or [],
        "min_budget": sponsor.min_budget,
        "max_budget": sponsor.max_budget,
    }

    explanation = await engine.explain_match_compatibility(project_dict, sponsor_dict)
    return explanation
