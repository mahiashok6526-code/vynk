import math
import re
from datetime import datetime
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional, require_entrepreneur
from app.models.user import User, UserRole, EntrepreneurProfile
from app.models.project import Project, ProjectRequirement, ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    FounderInfoRead,
    ProjectRequirementRead,
    ProjectPaginationResponse,
)

router = APIRouter()


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def format_project_response(p: Project) -> ProjectRead:
    founder = None
    if p.entrepreneur and p.entrepreneur.user:
        u = p.entrepreneur.user
        ts = u.trust_score.score if getattr(u, "trust_score", None) else 50
        founder = FounderInfoRead(
            id=p.entrepreneur.id,
            user_id=u.id,
            full_name=u.full_name,
            username=u.username,
            avatar_url=u.avatar_url,
            headline=u.headline,
            location=u.location,
            trust_score=ts,
            is_verified=u.is_verified,
        )

    # Sync website/demo and logo/cover if one is populated and the other is empty
    web_url = p.website_url or p.demo_url
    demo_url = p.demo_url or p.website_url
    logo_url = getattr(p, "logo_url", None) or p.cover_image_url
    cover_url = p.cover_image_url or getattr(p, "logo_url", None)

    reqs = [
        ProjectRequirementRead(
            id=r.id,
            project_id=r.project_id,
            requirement_type=r.requirement_type,
            title=r.title,
            description=r.description,
            amount=r.amount,
            is_fulfilled=r.is_fulfilled,
            created_at=r.created_at,
        )
        for r in (p.requirements or [])
    ]

    commitments_count = len(p.commitments) if getattr(p, "commitments", None) else 0

    return ProjectRead(
        id=p.id,
        slug=p.slug,
        entrepreneur_id=p.entrepreneur_id,
        title=p.title,
        tagline=p.tagline,
        description=p.description,
        category=p.category,
        industry=p.industry,
        stage=p.stage.value if hasattr(p.stage, "value") else str(p.stage),
        problem_statement=p.problem_statement,
        proposed_solution=p.proposed_solution,
        target_market=p.target_market,
        value_proposition=p.value_proposition,
        current_progress=p.current_progress,
        funding_goal=p.funding_goal,
        funding_received=p.funding_received if p.funding_received is not None else 0.0,
        current_funding=p.current_funding if p.current_funding is not None else (p.funding_received or 0.0),
        currency=getattr(p, "currency", "INR") or "INR",
        required_support=p.required_support or [],
        required_resources=p.required_resources,
        skills_needed=p.skills_needed or [],
        tech_stack=p.tech_stack or [],
        website_url=web_url,
        demo_url=demo_url,
        pitch_deck_url=p.pitch_deck_url,
        video_url=p.video_url,
        cover_image_url=cover_url,
        logo_url=logo_url,
        location=p.location,
        timeline=p.timeline,
        status=p.status.value if hasattr(p.status, "value") else str(p.status),
        created_at=p.created_at,
        updated_at=p.updated_at,
        requirements=reqs,
        founder=founder,
        commitments_count=commitments_count,
    )


def validate_showcase_fields(title: Optional[str], tagline: Optional[str], description: Optional[str],
                             category: Optional[str], stage: Optional[str],
                             problem_statement: Optional[str], proposed_solution: Optional[str],
                             target_market: Optional[str], value_proposition: Optional[str],
                             funding_goal: Optional[float], required_support: Optional[List[str]]):
    missing = []
    if not title or len(title.strip()) < 2:
        missing.append("Project Name / Title (min 2 characters)")
    if not tagline or len(tagline.strip()) < 5:
        missing.append("Tagline (min 5 characters)")
    if not description or len(description.strip()) < 10:
        missing.append("Detailed Description (min 10 characters)")
    if not category or not category.strip():
        missing.append("Category")
    if not stage:
        missing.append("Startup Stage")
    if not problem_statement or len(problem_statement.strip()) < 10:
        missing.append("Problem Statement (min 10 characters)")
    if not proposed_solution or len(proposed_solution.strip()) < 10:
        missing.append("Proposed Solution (min 10 characters)")
    if not target_market or len(target_market.strip()) < 5:
        missing.append("Target Users / Market (min 5 characters)")
    if not value_proposition or len(value_proposition.strip()) < 5:
        missing.append("Unique Value Proposition (min 5 characters)")
    if funding_goal is None or funding_goal <= 0:
        missing.append("Funding Goal (must be greater than 0)")
    if not required_support or len(required_support) == 0:
        missing.append("Required Support (select at least one type)")

    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish incomplete project showcase. Missing required fields: {', '.join(missing)}",
        )


@router.get("/", response_model=Union[ProjectPaginationResponse, List[ProjectRead]])
async def list_projects(
    category: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    required_support: Optional[str] = Query(None),
    min_funding: Optional[float] = Query(None),
    max_funding: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    sort: Optional[str] = Query("recent"),
    search: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Discover published projects available on Vynk with advanced database-level filtering, search, sorting and pagination."""
    base_conditions = []

    # Status handling: Drafts and Archived are NEVER shown in public discovery
    if status and status.lower() not in ["draft", "archived"]:
        base_conditions.append(Project.status == status.lower())
    else:
        public_statuses = [
            ProjectStatus.PUBLISHED,
            ProjectStatus.SEEKING_SPONSORSHIP,
            ProjectStatus.IN_DISCUSSION,
            ProjectStatus.FUNDED,
            ProjectStatus.COMPLETED,
            ProjectStatus.ACTIVE,
        ]
        base_conditions.append(Project.status.in_(public_statuses))

    if category:
        base_conditions.append(Project.category.ilike(f"%{category}%"))
    if industry:
        base_conditions.append(Project.industry.ilike(f"%{industry}%"))
    if stage:
        base_conditions.append(Project.stage == stage.lower())
    if min_funding is not None:
        base_conditions.append(Project.funding_goal >= min_funding)
    if max_funding is not None:
        base_conditions.append(Project.funding_goal <= max_funding)
    if location:
        base_conditions.append(Project.location.ilike(f"%{location}%"))
    if search:
        search_pattern = f"%{search}%"
        base_conditions.append(
            Project.title.ilike(search_pattern)
            | Project.tagline.ilike(search_pattern)
            | Project.description.ilike(search_pattern)
            | Project.category.ilike(search_pattern)
            | Project.industry.ilike(search_pattern)
        )
    if required_support:
        base_conditions.append(cast(Project.required_support, String).ilike(f"%{required_support}%"))

    # Database-level count query for pagination
    count_query = select(func.count(Project.id)).where(*base_conditions)
    count_res = await db.execute(count_query)
    total_count = count_res.scalar() or 0

    # Sorting
    order_clauses = []
    if sort == "updated":
        order_clauses.append(Project.updated_at.desc())
    elif sort == "funding_high":
        order_clauses.append(Project.funding_goal.desc())
    elif sort == "funding_low":
        order_clauses.append(Project.funding_goal.asc())
    elif sort == "progress":
        order_clauses.append(Project.funding_received.desc())
    elif sort == "title":
        order_clauses.append(Project.title.asc())
    else:  # "recent"
        order_clauses.append(Project.created_at.desc())

    query = (
        select(Project)
        .where(*base_conditions)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
        .order_by(*order_clauses)
    )

    if page is not None:
        eff_offset = (page - 1) * limit
        query = query.offset(eff_offset).limit(limit)
    else:
        query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    projects = result.scalars().all()
    formatted = [format_project_response(p) for p in projects]

    if page is not None:
        total_pages = math.ceil(total_count / limit) if limit > 0 else 1
        return ProjectPaginationResponse(
            results=formatted,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    return formatted


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Create a new project or startup showcase (Entrepreneurs only)."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    requested_status = data.status.lower() if data.status else None

    if requested_status == "draft":
        project_status = ProjectStatus.DRAFT
    elif requested_status in ["published", "seeking_sponsorship"]:
        validate_showcase_fields(
            title=data.title,
            tagline=data.tagline,
            description=data.description,
            category=data.category,
            stage=data.stage,
            problem_statement=data.problem_statement,
            proposed_solution=data.proposed_solution,
            target_market=data.target_market,
            value_proposition=data.value_proposition,
            funding_goal=data.funding_goal,
            required_support=data.required_support,
        )
        project_status = ProjectStatus(requested_status)
    else:
        # Backward compatibility: if problem & solution supplied, mark PUBLISHED; else ACTIVE
        if data.problem_statement and data.proposed_solution and data.target_market and data.value_proposition:
            project_status = ProjectStatus.PUBLISHED
        else:
            project_status = ProjectStatus.ACTIVE

    base_slug = slugify(data.title) or "project"
    slug = f"{base_slug}-{current_user.id}"

    # Ensure unique slug
    check = await db.execute(select(Project.id).where(Project.slug == slug))
    if check.scalar_one_or_none():
        slug = f"{base_slug}-{current_user.id}-{int(datetime.now().timestamp())}"

    demo_val = data.demo_url or data.website_url
    web_val = data.website_url or data.demo_url
    cover_val = data.cover_image_url or data.logo_url
    logo_val = data.logo_url or data.cover_image_url

    project = Project(
        entrepreneur_id=current_user.entrepreneur_profile.id,
        title=data.title.strip(),
        slug=slug,
        tagline=data.tagline.strip() if data.tagline else "",
        description=data.description.strip() if data.description else "",
        category=data.category or "CleanTech",
        industry=data.industry,
        stage=data.stage or "idea",
        problem_statement=data.problem_statement,
        proposed_solution=data.proposed_solution,
        target_market=data.target_market,
        value_proposition=data.value_proposition,
        current_progress=data.current_progress,
        funding_goal=float(data.funding_goal or 0.0),
        funding_received=float(data.funding_received or 0.0),
        current_funding=float(data.funding_received or 0.0),
        currency=data.currency or "INR",
        required_support=data.required_support or [],
        required_resources=data.required_resources,
        skills_needed=data.skills_needed or [],
        tech_stack=data.tech_stack or [],
        demo_url=demo_val,
        website_url=web_val,
        pitch_deck_url=data.pitch_deck_url,
        video_url=data.video_url,
        cover_image_url=cover_val,
        logo_url=logo_val,
        location=data.location,
        timeline=data.timeline,
        status=project_status,
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

    # Re-fetch with all relationships loaded
    query = (
        select(Project)
        .where(Project.id == project.id)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
    )
    res = await db.execute(query)
    full_proj = res.scalar_one()
    return format_project_response(full_proj)


@router.get("/my-projects", response_model=List[ProjectRead])
async def get_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Get all projects created by the authenticated entrepreneur (including drafts and archived)."""
    if not current_user.entrepreneur_profile:
        return []

    query = (
        select(Project)
        .where(Project.entrepreneur_id == current_user.entrepreneur_profile.id)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    projects = result.scalars().all()
    return [format_project_response(p) for p in projects]


@router.get("/{id_or_slug}", response_model=ProjectRead)
async def get_project(
    id_or_slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Retrieve full project details by ID or slug."""
    query = (
        select(Project)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
    )

    if id_or_slug.isdigit():
        query = query.where(Project.id == int(id_or_slug))
    else:
        query = query.where(Project.slug == id_or_slug)

    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    # If project is Draft, only project owner or Admin can view it
    is_draft = (
        project.status == ProjectStatus.DRAFT
        or str(project.status) == "draft"
        or (hasattr(project.status, "value") and project.status.value == "draft")
    )
    if is_draft:
        is_owner = (
            current_user
            and current_user.entrepreneur_profile
            and project.entrepreneur_id == current_user.entrepreneur_profile.id
        )
        is_admin = current_user and current_user.role == UserRole.ADMIN
        if not (is_owner or is_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

    return format_project_response(project)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Update project showcase details (Project owner only)."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    # Ownership check
    if project.entrepreneur_id != current_user.entrepreneur_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this project.",
        )

    # If transitioning from draft to published/seeking_sponsorship, validate required fields
    target_status = data.status.lower() if data.status else None
    if target_status in ["published", "seeking_sponsorship"] and project.status == ProjectStatus.DRAFT:
        eff_title = data.title if data.title is not None else project.title
        eff_tagline = data.tagline if data.tagline is not None else project.tagline
        eff_desc = data.description if data.description is not None else project.description
        eff_cat = data.category if data.category is not None else project.category
        eff_stage = data.stage if data.stage is not None else project.stage
        eff_prob = data.problem_statement if data.problem_statement is not None else project.problem_statement
        eff_sol = data.proposed_solution if data.proposed_solution is not None else project.proposed_solution
        eff_target = data.target_market if data.target_market is not None else project.target_market
        eff_val = data.value_proposition if data.value_proposition is not None else project.value_proposition
        eff_goal = data.funding_goal if data.funding_goal is not None else project.funding_goal
        eff_supp = data.required_support if data.required_support is not None else project.required_support

        validate_showcase_fields(
            title=eff_title,
            tagline=eff_tagline,
            description=eff_desc,
            category=eff_cat,
            stage=eff_stage,
            problem_statement=eff_prob,
            proposed_solution=eff_sol,
            target_market=eff_target,
            value_proposition=eff_val,
            funding_goal=eff_goal,
            required_support=eff_supp,
        )
        project.status = ProjectStatus(target_status)
    elif target_status:
        try:
            project.status = ProjectStatus(target_status)
        except ValueError:
            pass

    # Update individual fields if provided
    if data.title is not None:
        project.title = data.title.strip()
    if data.tagline is not None:
        project.tagline = data.tagline.strip()
    if data.description is not None:
        project.description = data.description.strip()
    if data.category is not None:
        project.category = data.category
    if data.industry is not None:
        project.industry = data.industry
    if data.stage is not None:
        project.stage = data.stage
    if data.problem_statement is not None:
        project.problem_statement = data.problem_statement
    if data.proposed_solution is not None:
        project.proposed_solution = data.proposed_solution
    if data.target_market is not None:
        project.target_market = data.target_market
    if data.value_proposition is not None:
        project.value_proposition = data.value_proposition
    if data.current_progress is not None:
        project.current_progress = data.current_progress
    if data.funding_goal is not None:
        project.funding_goal = float(data.funding_goal)
    if data.funding_received is not None:
        project.funding_received = float(data.funding_received)
        project.current_funding = float(data.funding_received)
    if data.currency is not None:
        project.currency = data.currency
    if data.required_support is not None:
        project.required_support = data.required_support
    if data.required_resources is not None:
        project.required_resources = data.required_resources
    if data.skills_needed is not None:
        project.skills_needed = data.skills_needed
    if data.tech_stack is not None:
        project.tech_stack = data.tech_stack
    if data.demo_url is not None or data.website_url is not None:
        val = data.demo_url or data.website_url
        project.demo_url = val
        project.website_url = val
    if data.pitch_deck_url is not None:
        project.pitch_deck_url = data.pitch_deck_url
    if data.video_url is not None:
        project.video_url = data.video_url
    if data.cover_image_url is not None or data.logo_url is not None:
        val = data.cover_image_url or data.logo_url
        project.cover_image_url = val
        project.logo_url = val
    if data.location is not None:
        project.location = data.location
    if data.timeline is not None:
        project.timeline = data.timeline

    # Update requirements if provided
    if data.requirements is not None:
        project.requirements.clear()
        for req in data.requirements:
            project.requirements.append(
                ProjectRequirement(
                    project_id=project.id,
                    requirement_type=req.requirement_type,
                    title=req.title,
                    description=req.description,
                    amount=req.amount,
                )
            )

    await db.commit()
    await db.refresh(project)
    return format_project_response(project)


@router.post("/{project_id}/publish", response_model=ProjectRead)
async def publish_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Publish a draft project showcase after validating all required fields."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.entrepreneur_id != current_user.entrepreneur_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to publish this project.",
        )

    validate_showcase_fields(
        title=project.title,
        tagline=project.tagline,
        description=project.description,
        category=project.category,
        stage=project.stage,
        problem_statement=project.problem_statement,
        proposed_solution=project.proposed_solution,
        target_market=project.target_market,
        value_proposition=project.value_proposition,
        funding_goal=project.funding_goal,
        required_support=project.required_support,
    )

    project.status = ProjectStatus.PUBLISHED
    await db.commit()
    await db.refresh(project)
    return format_project_response(project)


@router.post("/{project_id}/archive", response_model=ProjectRead)
async def archive_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Archive an existing project showcase."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user).selectinload(User.trust_score),
            selectinload(Project.commitments),
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.entrepreneur_id != current_user.entrepreneur_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to archive this project.",
        )

    project.status = ProjectStatus.ARCHIVED
    await db.commit()
    await db.refresh(project)
    return format_project_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_or_archive_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Delete a draft project or archive a published project."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not initialized.",
        )

    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.entrepreneur_id != current_user.entrepreneur_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project.",
        )

    if project.status == ProjectStatus.DRAFT:
        await db.delete(project)
        await db.commit()
        return {"detail": "Draft project deleted successfully."}
    else:
        project.status = ProjectStatus.ARCHIVED
        await db.commit()
        return {"detail": "Project archived successfully."}
