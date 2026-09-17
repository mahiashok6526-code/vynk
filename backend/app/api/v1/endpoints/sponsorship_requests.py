from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, require_entrepreneur, require_sponsor
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.sponsorship import (
    SponsorshipRequest,
    SponsorshipRequestStatus,
    SponsorshipCommitment,
    CommitmentStatus,
    CommitmentUpdate,
)
from app.schemas.sponsorship_request import (
    SponsorshipRequestCreate,
    SponsorshipRequestRespond,
    SponsorshipRequestRead,
    SponsorshipRequestSenderRead,
    SponsorshipRequestRecipientRead,
    SponsorshipRequestProjectRead,
)
from app.services.notification_service import NotificationService

router = APIRouter()


def _serialize_request(req: SponsorshipRequest) -> SponsorshipRequestRead:
    sender_read = None
    if req.sender:
        sender_read = SponsorshipRequestSenderRead(
            id=req.sender.id,
            full_name=req.sender.full_name,
            email=req.sender.email,
            avatar_url=req.sender.avatar_url,
        )

    recipient_read = None
    if req.recipient:
        org_name = req.recipient.sponsor_profile.organization_name if req.recipient.sponsor_profile else None
        recipient_read = SponsorshipRequestRecipientRead(
            id=req.recipient.id,
            full_name=req.recipient.full_name,
            organization_name=org_name,
            avatar_url=req.recipient.avatar_url,
        )

    project_read = None
    if req.project:
        project_read = SponsorshipRequestProjectRead(
            id=req.project.id,
            title=req.project.title,
            slug=req.project.slug,
            tagline=req.project.tagline,
            category=req.project.category,
            currency=req.project.currency,
        )

    return SponsorshipRequestRead(
        id=req.id,
        sender_id=req.sender_id,
        recipient_id=req.recipient_id,
        project_id=req.project_id,
        message=req.message,
        requested_amount=req.requested_amount,
        currency=req.currency or "INR",
        sponsorship_type=req.sponsorship_type,
        requested_resources=req.requested_resources,
        response_note=req.response_note,
        status=req.status.value,
        created_at=req.created_at,
        updated_at=req.updated_at,
        sender=sender_read,
        recipient=recipient_read,
        project=project_read,
        commitment_id=req.commitment.id if req.commitment else None,
    )


@router.post("/", response_model=SponsorshipRequestRead, status_code=status.HTTP_201_CREATED)
async def create_sponsorship_request(
    data: SponsorshipRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Entrepreneurs propose a sponsorship request to a verified sponsor."""
    if not current_user.entrepreneur_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entrepreneur profile not found.",
        )

    # Validate project ownership
    proj_q = select(Project).where(
        Project.id == data.project_id,
        Project.entrepreneur_id == current_user.entrepreneur_profile.id,
    )
    proj_res = await db.execute(proj_q)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you are not authorized to request sponsorship for this project.",
        )

    # Validate recipient is a sponsor
    recipient_q = (
        select(User)
        .where(User.id == data.recipient_id)
        .options(selectinload(User.sponsor_profile))
    )
    rec_res = await db.execute(recipient_q)
    recipient = rec_res.scalar_one_or_none()
    if not recipient or recipient.role != UserRole.SPONSOR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target sponsor user not found.",
        )

    # Prevent duplicate pending requests for the same project and sponsor
    dup_q = select(SponsorshipRequest).where(
        SponsorshipRequest.project_id == data.project_id,
        SponsorshipRequest.recipient_id == data.recipient_id,
        SponsorshipRequest.status == SponsorshipRequestStatus.PENDING,
    )
    dup_res = await db.execute(dup_q)
    if dup_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending sponsorship request already exists for this project and sponsor.",
        )

    req = SponsorshipRequest(
        sender_id=current_user.id,
        recipient_id=data.recipient_id,
        project_id=data.project_id,
        message=data.message.strip(),
        requested_amount=data.requested_amount,
        currency=data.currency or "INR",
        sponsorship_type=data.sponsorship_type,
        requested_resources=data.requested_resources.strip() if data.requested_resources else None,
        status=SponsorshipRequestStatus.PENDING,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    # Dispatch notification to recipient sponsor
    await NotificationService.create_notification(
        db=db,
        user_id=data.recipient_id,
        title=f"New Sponsorship Request: {project.title}",
        content=f"{current_user.full_name} submitted a sponsorship proposal for {project.title}.",
        type="sponsorship_request",
        entity_type="sponsorship_request",
        entity_id=req.id,
        link="/dashboard/sponsor",
    )

    # Load relationships
    load_q = (
        select(SponsorshipRequest)
        .where(SponsorshipRequest.id == req.id)
        .options(
            selectinload(SponsorshipRequest.sender),
            selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile),
            selectinload(SponsorshipRequest.project),
            selectinload(SponsorshipRequest.commitment),
        )
    )
    res = await db.execute(load_q)
    loaded_req = res.scalar_one()
    return _serialize_request(loaded_req)


@router.get("/", response_model=List[SponsorshipRequestRead])
async def list_sponsorship_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List sponsorship requests relevant to current user."""
    q = (
        select(SponsorshipRequest)
        .options(
            selectinload(SponsorshipRequest.sender),
            selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile),
            selectinload(SponsorshipRequest.project),
            selectinload(SponsorshipRequest.commitment),
        )
        .order_by(SponsorshipRequest.created_at.desc())
    )

    if current_user.role == UserRole.ENTREPRENEUR:
        q = q.where(SponsorshipRequest.sender_id == current_user.id)
    elif current_user.role == UserRole.SPONSOR:
        q = q.where(SponsorshipRequest.recipient_id == current_user.id)
    elif current_user.role != UserRole.ADMIN:
        return []

    if status_filter:
        q = q.where(SponsorshipRequest.status == status_filter.lower())
    if project_id:
        q = q.where(SponsorshipRequest.project_id == project_id)

    res = await db.execute(q)
    requests = res.scalars().all()
    return [_serialize_request(r) for r in requests]


@router.get("/{request_id}", response_model=SponsorshipRequestRead)
async def get_sponsorship_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single sponsorship request details."""
    q = (
        select(SponsorshipRequest)
        .where(SponsorshipRequest.id == request_id)
        .options(
            selectinload(SponsorshipRequest.sender),
            selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile),
            selectinload(SponsorshipRequest.project),
            selectinload(SponsorshipRequest.commitment),
        )
    )
    res = await db.execute(q)
    req = res.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship request not found.")

    # Strict authorization: must be sender, recipient, or admin
    if current_user.role != UserRole.ADMIN and req.sender_id != current_user.id and req.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship request not found.")

    return _serialize_request(req)


@router.post("/{request_id}/respond", response_model=SponsorshipRequestRead)
async def respond_to_sponsorship_request(
    request_id: int,
    data: SponsorshipRequestRespond,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_sponsor),
):
    """Sponsors accept or reject a sponsorship request.
    
    When accepted, creates a linked SponsorshipCommitment with initial status INTERESTED.
    """
    if not current_user.sponsor_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sponsor profile not initialized.")

    q = (
        select(SponsorshipRequest)
        .where(SponsorshipRequest.id == request_id)
        .options(
            selectinload(SponsorshipRequest.sender),
            selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile),
            selectinload(SponsorshipRequest.project),
            selectinload(SponsorshipRequest.commitment),
        )
    )
    res = await db.execute(q)
    req = res.scalar_one_or_none()
    if not req or req.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship request not found.")

    if req.status != SponsorshipRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot respond to request that is already {req.status.value}.",
        )

    if data.action == "accept":
        req.status = SponsorshipRequestStatus.ACCEPTED
        req.response_note = data.response_note or "Sponsor accepted request."

        # Create linked commitment in INTERESTED status (Correction #2)
        comm_amount = data.commitment_amount if data.commitment_amount is not None else (req.requested_amount or 0.0)
        commitment = SponsorshipCommitment(
            project_id=req.project_id,
            sponsor_id=current_user.sponsor_profile.id,
            entrepreneur_id=req.project.entrepreneur_id,
            request_id=req.id,
            title=f"{req.sponsorship_type} for {req.project.title}",
            description=req.message,
            amount=comm_amount,
            currency=req.currency or "INR",
            sponsorship_type=req.sponsorship_type,
            status=CommitmentStatus.INTERESTED,
            expected_date=data.expected_date,
            notes=data.response_note or f"Accepted request #{req.id}.",
        )
        db.add(commitment)
        await db.flush()

        initial_update = CommitmentUpdate(
            commitment_id=commitment.id,
            updated_by=current_user.id,
            update_type="status_change",
            title="Commitment Initiated",
            previous_status="none",
            new_status=CommitmentStatus.INTERESTED.value,
            note=f"Commitment initiated with status '{CommitmentStatus.INTERESTED.value}' following accepted sponsorship request #{req.id}.",
        )
        db.add(initial_update)

    elif data.action == "reject":
        req.status = SponsorshipRequestStatus.REJECTED
        req.response_note = data.response_note or "Sponsor declined request."

    # Check response timeliness for Trust Score (Correction 2: < 48 hours response)
    req_time = req.created_at if req.created_at.tzinfo else req.created_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if (now - req_time).total_seconds() <= 48 * 3600:
        from app.services.trust_service import TrustService
        await TrustService.record_event(
            db=db,
            user_id=current_user.id,
            event_type="timely_response",
            impact=2,
            reason=f"Timely response (<48h) to sponsorship request #{req.id}.",
            reference_type="sponsorship_request",
            reference_id=req.id,
        )

    await db.commit()

    # Dispatch notification to entrepreneur
    if data.action == "accept":
        await NotificationService.create_notification(
            db=db,
            user_id=req.sender_id,
            title="Sponsorship Request Accepted!",
            content=f"{current_user.full_name} accepted your sponsorship proposal for {req.project.title}.",
            type="sponsorship_request",
            entity_type="sponsorship_request",
            entity_id=req.id,
            link=f"/commitments/{commitment.id}" if commitment else "/dashboard/entrepreneur",
        )
    elif data.action == "reject":
        await NotificationService.create_notification(
            db=db,
            user_id=req.sender_id,
            title="Sponsorship Request Declined",
            content=f"Your sponsorship proposal for {req.project.title} was declined by the sponsor.",
            type="sponsorship_request",
            entity_type="sponsorship_request",
            entity_id=req.id,
            link="/dashboard/entrepreneur",
        )

    db.expire_all()

    # Re-fetch with fresh relations
    res = await db.execute(q)
    updated_req = res.scalar_one()
    serialized = _serialize_request(updated_req)
    if data.action == "accept" and commitment:
        serialized.commitment_id = commitment.id
    return serialized



@router.post("/{request_id}/cancel", response_model=SponsorshipRequestRead)
async def cancel_sponsorship_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_entrepreneur),
):
    """Entrepreneurs cancel their own pending sponsorship request."""
    q = (
        select(SponsorshipRequest)
        .where(SponsorshipRequest.id == request_id)
        .options(
            selectinload(SponsorshipRequest.sender),
            selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile),
            selectinload(SponsorshipRequest.project),
            selectinload(SponsorshipRequest.commitment),
        )
    )
    res = await db.execute(q)
    req = res.scalar_one_or_none()
    if not req or req.sender_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship request not found.")

    if req.status != SponsorshipRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only pending requests can be cancelled. Current status is {req.status.value}.",
        )

    req.status = SponsorshipRequestStatus.CANCELLED
    req.response_note = "Cancelled by entrepreneur."
    await db.commit()
    await db.refresh(req)

    # Dispatch notification to recipient sponsor
    await NotificationService.create_notification(
        db=db,
        user_id=req.recipient_id,
        title="Sponsorship Request Cancelled",
        content=f"The sponsorship request for {req.project.title} was cancelled by the entrepreneur.",
        type="sponsorship_request",
        entity_type="sponsorship_request",
        entity_id=req.id,
        link="/dashboard/sponsor",
    )

    res = await db.execute(q)
    updated_req = res.scalar_one()
    return _serialize_request(updated_req)
