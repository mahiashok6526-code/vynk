from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, SponsorProfile
from app.models.project import Project
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
    """Returns AI service layer configuration and readiness for Phase 2 integration."""
    return {
        "status": "ready",
        "provider": settings.AI_PROVIDER,
        "gemini_ready": gemini_service.is_configured,
        "mode": "deterministic_compatibility_v1",
        "phase": 1,
        "notes": "Clean pluggable service architecture active. Live Gemini multimodal reasoning ready for Phase 2."
    }


@router.post("/match", summary="Get Explainable Matches for Project")
async def match_project_with_sponsors(
    data: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute compatibility rankings between a project and available sponsors."""
    # Fetch project
    project_q = select(Project).where(Project.id == data.project_id)
    project_res = await db.execute(project_q)
    project = project_res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    # Fetch active sponsors
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


@router.post("/explain", summary="Explain Match Factors")
async def explain_match(
    data: MatchExplanationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Provides a transparent, auditable breakdown of matching factors between project and sponsor."""
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
