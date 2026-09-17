from datetime import datetime, timezone
from typing import List, Optional, Set
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_sponsor
from app.models.user import User, UserRole, SponsorProfile, EntrepreneurProfile
from app.models.project import Project
from app.models.sponsorship import SponsorshipCommitment, CommitmentUpdate, CommitmentStatus
from app.schemas.commitment import (
    CommitmentCreate,
    CommitmentStatusUpdate,
    CommitmentRead,
    CommitmentMilestoneCreate,
    CommitmentUpdateRead,
)
from app.services.trust_service import TrustService
from app.services.notification_service import NotificationService

router = APIRouter()

# Controlled Status Lifecycle State Machine
VALID_TRANSITIONS = {
    CommitmentStatus.INTERESTED.value: [CommitmentStatus.DISCUSSION.value, CommitmentStatus.CANCELLED.value],
    CommitmentStatus.DISCUSSION.value: [CommitmentStatus.PROMISED.value, CommitmentStatus.CANCELLED.value],
    CommitmentStatus.PROMISED.value: [CommitmentStatus.CONFIRMED.value, CommitmentStatus.CANCELLED.value],
    CommitmentStatus.CONFIRMED.value: [CommitmentStatus.AGREEMENT.value, CommitmentStatus.CANCELLED.value],
    CommitmentStatus.AGREEMENT.value: [CommitmentStatus.FUNDED.value, CommitmentStatus.CANCELLED.value],
    CommitmentStatus.FUNDED.value: [CommitmentStatus.COMPLETED.value],
    CommitmentStatus.COMPLETED.value: [],
    CommitmentStatus.CANCELLED.value: [],
}

# Role permissions for specific transitions
ROLE_TRANSITION_PERMISSIONS = {
    CommitmentStatus.PROMISED.value: {UserRole.SPONSOR, UserRole.ADMIN},
    CommitmentStatus.FUNDED.value: {UserRole.SPONSOR, UserRole.ADMIN},
}


def _check_commitment_access(comm: SponsorshipCommitment, current_user: User) -> bool:
    """Verifies that the user is the sponsor, entrepreneur, or admin on this commitment."""
    if current_user.role == UserRole.ADMIN:
        return True
    if current_user.role == UserRole.SPONSOR and current_user.sponsor_profile:
        return comm.sponsor_id == current_user.sponsor_profile.id
    if current_user.role == UserRole.ENTREPRENEUR and current_user.entrepreneur_profile:
        return comm.entrepreneur_id == current_user.entrepreneur_profile.id
    return False


def _serialize_update(upd: CommitmentUpdate) -> CommitmentUpdateRead:
    updater_name = upd.updater.full_name if upd.updater else None
    updater_role = upd.updater.role.value if upd.updater and hasattr(upd.updater.role, "value") else str(upd.updater.role) if upd.updater else None
    return CommitmentUpdateRead(
        id=upd.id,
        commitment_id=upd.commitment_id,
        updated_by=upd.updated_by,
        update_type=upd.update_type or "status_change",
        title=upd.title,
        previous_status=upd.previous_status,
        new_status=upd.new_status,
        note=upd.note,
        evidence_reference=upd.evidence_reference,
        event_date=upd.event_date,
        created_at=upd.created_at,
        updater_name=updater_name,
        updater_role=updater_role,
    )


def _serialize_commitment(comm: SponsorshipCommitment) -> CommitmentRead:
    now = datetime.now(timezone.utc)
    is_overdue = False
    if comm.follow_up_date:
        fu = comm.follow_up_date if comm.follow_up_date.tzinfo else comm.follow_up_date.replace(tzinfo=timezone.utc)
        if fu < now and comm.status not in [CommitmentStatus.COMPLETED, CommitmentStatus.CANCELLED]:
            is_overdue = True

    project_title = comm.project.title if comm.project else None
    project_slug = comm.project.slug if comm.project else None

    sponsor_name = comm.sponsor.user.full_name if comm.sponsor and comm.sponsor.user else None
    sponsor_org = comm.sponsor.organization_name if comm.sponsor else None
    sponsor_avatar = comm.sponsor.user.avatar_url if comm.sponsor and comm.sponsor.user else None

    entrepreneur_name = comm.entrepreneur.user.full_name if comm.entrepreneur and comm.entrepreneur.user else None
    entrepreneur_avatar = comm.entrepreneur.user.avatar_url if comm.entrepreneur and comm.entrepreneur.user else None

    updates_read = [_serialize_update(u) for u in (comm.updates or [])]

    return CommitmentRead(
        id=comm.id,
        project_id=comm.project_id,
        sponsor_id=comm.sponsor_id,
        entrepreneur_id=comm.entrepreneur_id,
        request_id=comm.request_id,
        title=comm.title,
        description=comm.description,
        amount=comm.amount or 0.0,
        currency=comm.currency or "INR",
        sponsorship_type=comm.sponsorship_type,
        status=comm.status.value,
        expected_date=comm.expected_date,
        follow_up_date=comm.follow_up_date,
        follow_up_reason=comm.follow_up_reason,
        agreement_reference=comm.agreement_reference,
        cancellation_type=comm.cancellation_type,
        notes=comm.notes,
        created_at=comm.created_at,
        updated_at=comm.updated_at,
        updates=updates_read,
        project_title=project_title,
        project_slug=project_slug,
        sponsor_name=sponsor_name,
        sponsor_org=sponsor_org,
        sponsor_avatar=sponsor_avatar,
        entrepreneur_name=entrepreneur_name,
        entrepreneur_avatar=entrepreneur_avatar,
        is_overdue=is_overdue,
    )


def _base_commitment_query():
    return (
        select(SponsorshipCommitment)
        .options(
            selectinload(SponsorshipCommitment.updates).selectinload(CommitmentUpdate.updater),
            selectinload(SponsorshipCommitment.project),
            selectinload(SponsorshipCommitment.sponsor).selectinload(SponsorProfile.user),
            selectinload(SponsorshipCommitment.entrepreneur).selectinload(EntrepreneurProfile.user),
        )
    )


@router.get("/", response_model=List[CommitmentRead])
async def list_commitments(
    status_filter: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List commitments relevant to current user (as sponsor or entrepreneur)."""
    query = _base_commitment_query().order_by(SponsorshipCommitment.created_at.desc())

    if current_user.role == UserRole.SPONSOR and current_user.sponsor_profile:
        query = query.where(SponsorshipCommitment.sponsor_id == current_user.sponsor_profile.id)
    elif current_user.role == UserRole.ENTREPRENEUR and current_user.entrepreneur_profile:
        query = query.where(SponsorshipCommitment.entrepreneur_id == current_user.entrepreneur_profile.id)
    elif current_user.role != UserRole.ADMIN:
        return []

    if status_filter:
        query = query.where(SponsorshipCommitment.status == status_filter.lower())
    if project_id:
        query = query.where(SponsorshipCommitment.project_id == project_id)

    result = await db.execute(query)
    commitments = result.scalars().all()
    return [_serialize_commitment(c) for c in commitments]


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

    # Clean amount and currency
    amount_val = data.amount if data.amount is not None else 0.0
    currency_val = data.currency or "INR"

    commitment = SponsorshipCommitment(
        project_id=data.project_id,
        sponsor_id=current_user.sponsor_profile.id,
        entrepreneur_id=project.entrepreneur_id,
        request_id=data.request_id,
        title=data.title or f"{data.sponsorship_type} for {project.title}",
        description=data.description or data.notes,
        amount=amount_val,
        currency=currency_val,
        sponsorship_type=data.sponsorship_type,
        status=CommitmentStatus(data.status.lower()),
        expected_date=data.expected_date,
        follow_up_date=data.follow_up_date,
        follow_up_reason=data.follow_up_reason,
        agreement_reference=data.agreement_reference,
        notes=data.notes,
    )
    db.add(commitment)
    await db.flush()

    # Create initial audit history update
    formatted_amount = f"₹{amount_val:,.2f}" if currency_val == "INR" else f"{currency_val} {amount_val:,.2f}"
    initial_update = CommitmentUpdate(
        commitment_id=commitment.id,
        updated_by=current_user.id,
        update_type="status_change",
        title="Commitment Initiated",
        previous_status="none",
        new_status=commitment.status.value,
        note=f"Commitment initiated with status '{commitment.status.value}' for {formatted_amount} ({data.sponsorship_type}).",
    )
    db.add(initial_update)
    await db.commit()

    # Re-fetch full object with relations
    q = _base_commitment_query().where(SponsorshipCommitment.id == commitment.id)
    res = await db.execute(q)
    return _serialize_commitment(res.scalar_one())


@router.get("/follow-ups", response_model=List[CommitmentRead])
async def get_follow_ups_due(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve commitments requiring follow-up."""
    query = (
        _base_commitment_query()
        .where(
            SponsorshipCommitment.follow_up_date.isnot(None),
            SponsorshipCommitment.status.notin_([CommitmentStatus.COMPLETED, CommitmentStatus.CANCELLED])
        )
        .order_by(SponsorshipCommitment.follow_up_date.asc())
    )

    if current_user.role == UserRole.SPONSOR and current_user.sponsor_profile:
        query = query.where(SponsorshipCommitment.sponsor_id == current_user.sponsor_profile.id)
    elif current_user.role == UserRole.ENTREPRENEUR and current_user.entrepreneur_profile:
        query = query.where(SponsorshipCommitment.entrepreneur_id == current_user.entrepreneur_profile.id)
    elif current_user.role != UserRole.ADMIN:
        return []

    res = await db.execute(query)
    commitments = res.scalars().all()

    # Dispatch follow-up notifications if due
    now_utc = datetime.now(timezone.utc)
    for c in commitments:
        f_date = c.follow_up_date
        if f_date and f_date.tzinfo is None:
            f_date = f_date.replace(tzinfo=timezone.utc)
        if f_date and f_date <= now_utc:
            reason = c.follow_up_reason or "Scheduled progress follow-up"
            await NotificationService.create_notification(
                db=db,
                user_id=current_user.id,
                title=f"Follow-up Due: Commitment #{c.id}",
                content=f"Follow-up is due for commitment '{c.title}': {reason}.",
                type="follow_up",
                entity_type="commitment",
                entity_id=c.id,
                link=f"/commitments/{c.id}",
            )

    return [_serialize_commitment(c) for c in commitments]


@router.get("/{commitment_id}", response_model=CommitmentRead)
async def get_commitment(
    commitment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed commitment record with full updates and audit history."""
    q = _base_commitment_query().where(SponsorshipCommitment.id == commitment_id)
    res = await db.execute(q)
    commitment = res.scalar_one_or_none()
    if not commitment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    if not _check_commitment_access(commitment, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    return _serialize_commitment(commitment)


@router.patch("/{commitment_id}/status", response_model=CommitmentRead)
async def update_commitment_status(
    commitment_id: int,
    data: CommitmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Progress commitment through the controlled status lifecycle:
    
    INTERESTED -> DISCUSSION -> PROMISED -> CONFIRMED -> AGREEMENT -> FUNDED -> COMPLETED
    or CANCELLED from pre-completed states.
    """
    q = _base_commitment_query().where(SponsorshipCommitment.id == commitment_id)
    res = await db.execute(q)
    commitment = res.scalar_one_or_none()
    if not commitment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    if not _check_commitment_access(commitment, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    prev_status = commitment.status.value
    new_status = data.new_status.lower()

    # Terminal state protection
    if prev_status in [CommitmentStatus.COMPLETED.value, CommitmentStatus.CANCELLED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition commitment from terminal state '{prev_status}'.",
        )

    # Lifecycle state machine validation
    allowed_next = VALID_TRANSITIONS.get(prev_status, [])
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{prev_status}' to '{new_status}'. Allowed transitions: {', '.join(allowed_next) if allowed_next else 'None'}.",
        )

    # Role permission check
    required_roles = ROLE_TRANSITION_PERMISSIONS.get(new_status)
    if required_roles and current_user.role not in required_roles:
        roles_str = " or ".join([r.value for r in required_roles])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {roles_str} can advance commitment to '{new_status}'.",
        )

    commitment.status = CommitmentStatus(new_status)

    if data.follow_up_date is not None:
        commitment.follow_up_date = data.follow_up_date
    if data.follow_up_reason is not None:
        commitment.follow_up_reason = data.follow_up_reason
    if data.agreement_reference is not None:
        commitment.agreement_reference = data.agreement_reference
    if data.cancellation_type is not None:
        commitment.cancellation_type = data.cancellation_type

    # Record update entry
    update_entry = CommitmentUpdate(
        commitment_id=commitment.id,
        updated_by=current_user.id,
        update_type="status_change",
        title=f"Status: {prev_status.upper()} → {new_status.upper()}",
        previous_status=prev_status,
        new_status=new_status,
        cancellation_type=data.cancellation_type,
        note=data.note.strip(),
    )
    db.add(update_entry)

    # Factual Trust Score event hook on completion (Correction 1 & 3)
    if new_status == CommitmentStatus.COMPLETED.value and prev_status != CommitmentStatus.COMPLETED.value:
        fmt_amt = f"₹{commitment.amount:,.0f}" if commitment.currency == "INR" else f"{commitment.currency} {commitment.amount:,.0f}"
        
        # Award +5 to Sponsor for funding and fulfilling support
        if commitment.sponsor and commitment.sponsor.user_id:
            await TrustService.record_event(
                db=db,
                user_id=commitment.sponsor.user_id,
                event_type="commitment_completed",
                impact=5,
                reason=f"Successfully fulfilled sponsorship commitment #{commitment.id} ({fmt_amt}).",
                reference_type="commitment",
                reference_id=commitment.id,
            )
        # Award +5 to Entrepreneur for fulfilling venture deliverables
        if commitment.entrepreneur and commitment.entrepreneur.user_id:
            await TrustService.record_event(
                db=db,
                user_id=commitment.entrepreneur.user_id,
                event_type="commitment_completed",
                impact=5,
                reason=f"Successfully delivered venture commitment #{commitment.id} ({fmt_amt}).",
                reference_type="commitment",
                reference_id=commitment.id,
            )
    elif new_status == CommitmentStatus.CANCELLED.value:
        confirmed_states = [CommitmentStatus.CONFIRMED.value, CommitmentStatus.AGREEMENT.value, CommitmentStatus.FUNDED.value]
        if prev_status in confirmed_states and data.cancellation_type == "unilateral":
            # Unilateral cancellation on a confirmed deal incurs penalty to responsible party
            await TrustService.record_event(
                db=db,
                user_id=current_user.id,
                event_type="commitment_cancelled_unilateral",
                impact=-10,
                reason=f"Unilaterally cancelled confirmed commitment #{commitment.id}: {data.note[:100]}",
                reference_type="commitment",
                reference_id=commitment.id,
            )
        else:
            # Amicable / mutual cancellation or exploratory stage cancellation (0 penalty)
            cancel_mode = data.cancellation_type or ("exploratory" if prev_status not in confirmed_states else "mutual")
            await TrustService.record_event(
                db=db,
                user_id=current_user.id,
                event_type="commitment_cancelled_mutual",
                impact=0,
                reason=f"Commitment #{commitment.id} cancelled ({cancel_mode}): {data.note[:100]}",
                reference_type="commitment",
                reference_id=commitment.id,
            )

    await db.commit()

    # Dispatch event-driven notifications to participants
    sponsor_user_id = commitment.sponsor.user_id if commitment.sponsor else None
    ent_user_id = commitment.entrepreneur.user_id if commitment.entrepreneur else None
    other_user_id = ent_user_id if current_user.id == sponsor_user_id else sponsor_user_id

    if new_status == CommitmentStatus.COMPLETED.value:
        if sponsor_user_id:
            await NotificationService.create_notification(
                db=db,
                user_id=sponsor_user_id,
                title="Commitment Completed!",
                content=f"Commitment #{commitment.id} ({commitment.title}) has reached COMPLETED status. +5 Trust Score awarded!",
                type="commitment",
                entity_type="commitment",
                entity_id=commitment.id,
                link=f"/commitments/{commitment.id}",
            )
        if ent_user_id:
            await NotificationService.create_notification(
                db=db,
                user_id=ent_user_id,
                title="Commitment Completed!",
                content=f"Commitment #{commitment.id} ({commitment.title}) has reached COMPLETED status. +5 Trust Score awarded!",
                type="commitment",
                entity_type="commitment",
                entity_id=commitment.id,
                link=f"/commitments/{commitment.id}",
            )
    elif new_status == CommitmentStatus.CANCELLED.value:
        if other_user_id:
            await NotificationService.create_notification(
                db=db,
                user_id=other_user_id,
                title="Commitment Cancelled",
                content=f"Commitment #{commitment.id} was cancelled.",
                type="commitment",
                entity_type="commitment",
                entity_id=commitment.id,
                link=f"/commitments/{commitment.id}",
            )
    else:
        if other_user_id:
            await NotificationService.create_notification(
                db=db,
                user_id=other_user_id,
                title=f"Commitment Status: {new_status.upper()}",
                content=f"Commitment #{commitment.id} progressed from {prev_status.upper()} to {new_status.upper()}.",
                type="commitment",
                entity_type="commitment",
                entity_id=commitment.id,
                link=f"/commitments/{commitment.id}",
            )

    # Re-fetch
    res = await db.execute(q)
    return _serialize_commitment(res.scalar_one())


@router.post("/{commitment_id}/updates", response_model=CommitmentUpdateRead, status_code=status.HTTP_201_CREATED)
async def add_commitment_milestone_update(
    commitment_id: int,
    data: CommitmentMilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a structured milestone or progress update to a commitment."""
    q = (
        select(SponsorshipCommitment)
        .where(SponsorshipCommitment.id == commitment_id)
        .options(
            selectinload(SponsorshipCommitment.updates),
            selectinload(SponsorshipCommitment.entrepreneur),
            selectinload(SponsorshipCommitment.sponsor),
        )
    )
    res = await db.execute(q)
    commitment = res.scalar_one_or_none()
    if not commitment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    if not _check_commitment_access(commitment, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    upd = CommitmentUpdate(
        commitment_id=commitment.id,
        updated_by=current_user.id,
        update_type=data.update_type,
        title=data.title.strip(),
        previous_status=commitment.status.value,
        new_status=commitment.status.value,
        note=data.note.strip(),
        evidence_reference=data.evidence_reference.strip() if data.evidence_reference else None,
        event_date=data.event_date or datetime.now(timezone.utc),
    )
    db.add(upd)
    await db.commit()
    await db.refresh(upd)

    # Award milestone trust points if evidence provided and under cap (max 2 per commitment)
    if data.update_type == "milestone" and data.evidence_reference:
        from app.models.trust import TrustScoreEvent
        from sqlalchemy import func
        comm_milestone_ref = f"commitment_milestone_{commitment.id}"
        existing_milestones_q = select(func.count(TrustScoreEvent.id)).where(
            TrustScoreEvent.event_type == "milestone_completed",
            TrustScoreEvent.reference_type == comm_milestone_ref,
        )
        existing_count = await db.scalar(existing_milestones_q) or 0
        if existing_count < 2:
            ent_user_id = commitment.entrepreneur.user_id if commitment.entrepreneur else None
            if ent_user_id:
                await TrustService.record_event(
                    db=db,
                    user_id=ent_user_id,
                    event_type="milestone_completed",
                    impact=2,
                    reason=f"Verified milestone delivered on commitment #{commitment.id}: '{data.title[:80]}'.",
                    reference_type=comm_milestone_ref,
                    reference_id=upd.id,
                )

    # Dispatch notification to other party
    sponsor_user_id = commitment.sponsor.user_id if commitment.sponsor else None
    ent_user_id = commitment.entrepreneur.user_id if commitment.entrepreneur else None
    other_user_id = ent_user_id if current_user.id == sponsor_user_id else sponsor_user_id
    if other_user_id:
        await NotificationService.create_notification(
            db=db,
            user_id=other_user_id,
            title="Commitment Milestone Update",
            content=f"New {data.update_type} recorded on commitment #{commitment.id}: {data.title.strip()}.",
            type="milestone",
            entity_type="commitment",
            entity_id=commitment.id,
            link=f"/commitments/{commitment.id}",
        )

    # Re-fetch with updater loaded
    uq = select(CommitmentUpdate).where(CommitmentUpdate.id == upd.id).options(selectinload(CommitmentUpdate.updater))
    ures = await db.execute(uq)
    loaded_upd = ures.scalar_one()
    return _serialize_update(loaded_upd)


@router.get("/{commitment_id}/updates", response_model=List[CommitmentUpdateRead])
async def list_commitment_updates(
    commitment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full timeline of updates and status history for a commitment."""
    q = (
        select(SponsorshipCommitment)
        .where(SponsorshipCommitment.id == commitment_id)
    )
    res = await db.execute(q)
    commitment = res.scalar_one_or_none()
    if not commitment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    if not _check_commitment_access(commitment, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment record not found.")

    uq = (
        select(CommitmentUpdate)
        .where(CommitmentUpdate.commitment_id == commitment_id)
        .options(selectinload(CommitmentUpdate.updater))
        .order_by(CommitmentUpdate.created_at.desc())
    )
    ures = await db.execute(uq)
    updates = ures.scalars().all()
    return [_serialize_update(u) for u in updates]
