from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_sponsor
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.sponsorship import SponsorshipCommitment, CommitmentUpdate, CommitmentStatus
from app.schemas.commitment import CommitmentCreate, CommitmentStatusUpdate, CommitmentRead
from app.services.trust_service import TrustService

router = APIRouter()


@router.get("/", response_model=List[CommitmentRead])
async def list_commitments(
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List commitments relevant to current user (as sponsor or entrepreneur)."""
    query = (
        select(SponsorshipCommitment)
        .options(selectinload(SponsorshipCommitment.updates))
        .order_by(SponsorshipCommitment.created_at.desc())
    )

    if current_user.role == UserRole.SPONSOR and current_user.sponsor_profile:
        query = query.where(SponsorshipCommitment.sponsor_id == current_user.sponsor_profile.id)
    elif current_user.role == UserRole.ENTREPRENEUR and current_user.entrepreneur_profile:
        query = query.where(SponsorshipCommitment.entrepreneur_id == current_user.entrepreneur_profile.id)

    if status_filter:
        query = query.where(SponsorshipCommitment.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=CommitmentRead, status_code=status.HTTP_201_CREATED)
async def create_commitment(
    data: CommitmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_sponsor),
):
    """Create a structured sponsorship commitment (Sponsors only)."""
    if not current_user.sponsor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsor profile not initialized.",
        )

    # Validate project existence
    project_query = select(Project).where(Project.id == data.project_id)
    project_res = await db.execute(project_query)
    project = project_res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target project not found.",
        )

    commitment = SponsorshipCommitment(
        project_id=data.project_id,
        sponsor_id=current_user.sponsor_profile.id,
        entrepreneur_id=project.entrepreneur_id,
        amount=data.amount,
        sponsorship_type=data.sponsorship_type,
        status=CommitmentStatus(data.status),
        expected_date=data.expected_date,
        follow_up_date=data.follow_up_date,
        agreement_reference=data.agreement_reference,
        notes=data.notes,
    )
    db.add(commitment)
    await db.flush()

    # Create initial audit history update
    initial_update = CommitmentUpdate(
        commitment_id=commitment.id,
        updated_by=current_user.id,
        previous_status="none",
        new_status=commitment.status.value,
        note=f"Commitment initiated with status '{commitment.status.value}' for ${commitment.amount:,.2f}.",
    )
    db.add(initial_update)
    await db.commit()

    # Re-fetch with updates
    q = (
        select(SponsorshipCommitment)
        .where(SponsorshipCommitment.id == commitment.id)
        .options(selectinload(SponsorshipCommitment.updates))
    )
    res = await db.execute(q)
    return res.scalar_one()


@router.patch("/{commitment_id}/status", response_model=CommitmentRead)
async def update_commitment_status(
    commitment_id: int,
    data: CommitmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Progress commitment through the structured lifecycle:

    Interested → Discussion → Promised → Confirmed → Agreement → Funded → Completed
    """
    q = (
        select(SponsorshipCommitment)
        .where(SponsorshipCommitment.id == commitment_id)
        .options(selectinload(SponsorshipCommitment.updates))
    )
    res = await db.execute(q)
    commitment = res.scalar_one_or_none()
    if not commitment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commitment record not found.",
        )

    prev_status = commitment.status.value
    new_status = data.new_status
    commitment.status = CommitmentStatus(new_status)

    if data.follow_up_date:
        commitment.follow_up_date = data.follow_up_date
    if data.agreement_reference:
        commitment.agreement_reference = data.agreement_reference

    # Record update entry
    update_entry = CommitmentUpdate(
        commitment_id=commitment.id,
        updated_by=current_user.id,
        previous_status=prev_status,
        new_status=new_status,
        note=data.note,
    )
    db.add(update_entry)

    # Check if commitment completed to grant Trust Score reward
    if new_status == CommitmentStatus.COMPLETED.value and prev_status != CommitmentStatus.COMPLETED.value:
        await TrustService.record_event(
            db=db,
            user_id=current_user.id,
            event_type="commitment_completed",
            impact=5,
            reason=f"Successfully fulfilled sponsorship commitment #{commitment.id} (${commitment.amount:,.0f}).",
        )

    await db.commit()
    await db.refresh(commitment)
    return commitment


@router.get("/follow-ups", response_model=List[CommitmentRead])
async def get_follow_ups_due(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve commitments requiring follow-up."""
    now = datetime.now(timezone.utc)
    query = (
        select(SponsorshipCommitment)
        .where(
            SponsorshipCommitment.follow_up_date.isnot(None),
            SponsorshipCommitment.status.notin_([CommitmentStatus.COMPLETED, CommitmentStatus.CANCELLED])
        )
        .options(selectinload(SponsorshipCommitment.updates))
        .order_by(SponsorshipCommitment.follow_up_date.asc())
    )

    if current_user.role == UserRole.SPONSOR and current_user.sponsor_profile:
        query = query.where(SponsorshipCommitment.sponsor_id == current_user.sponsor_profile.id)
    elif current_user.role == UserRole.ENTREPRENEUR and current_user.entrepreneur_profile:
        query = query.where(SponsorshipCommitment.entrepreneur_id == current_user.entrepreneur_profile.id)

    res = await db.execute(query)
    return res.scalars().all()
