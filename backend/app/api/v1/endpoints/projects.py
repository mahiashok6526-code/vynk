import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_entrepreneur
from app.models.user import User, UserRole
from app.models.project import Project, ProjectRequirement, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter()


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


@router.get("/", response_model=List[ProjectRead])
async def list_projects(
    category: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = 50,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Discover projects available on Vynk."""
    query = (
        select(Project)
        .where(Project.status == ProjectStatus.ACTIVE)
        .options(selectinload(Project.requirements))
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    if category:
        query = query.where(Project.category.ilike(f"%{category}%"))
    if stage:
        query = query.where(Project.stage == stage)
    if search:
        query = query.where(
            Project.title.ilike(f"%{search}%") | Project.tagline.ilike(f"%{search}%")
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Create a new project/startup showcase (Entrepreneurs only)."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    base_slug = slugify(data.title)
    slug = f"{base_slug}-{current_user.id}"

    project = Project(
        entrepreneur_id=current_user.entrepreneur_profile.id,
        title=data.title,
        slug=slug,
        tagline=data.tagline,
        description=data.description,
        category=data.category,
        stage=data.stage,
        funding_goal=data.funding_goal,
        demo_url=data.demo_url,
        pitch_deck_url=data.pitch_deck_url,
        status=ProjectStatus.ACTIVE,
    )
    db.add(project)
    await db.flush()

    for req in data.requirements:
        r = ProjectRequirement(
            project_id=project.id,
            requirement_type=req.requirement_type,
            title=req.title,
            description=req.description,
            amount=req.amount,
        )
        db.add(r)

    await db.commit()
    await db.refresh(project)

    # Re-fetch with requirements loaded
    query = (
        select(Project)
        .where(Project.id == project.id)
        .options(selectinload(Project.requirements))
    )
    res = await db.execute(query)
    return res.scalar_one()


@router.get("/my-projects", response_model=List[ProjectRead])
async def get_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Get all projects created by the authenticated entrepreneur."""
    if not current_user.entrepreneur_profile:
        return []

    query = (
        select(Project)
        .where(Project.entrepreneur_id == current_user.entrepreneur_profile.id)
        .options(selectinload(Project.requirements))
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()
