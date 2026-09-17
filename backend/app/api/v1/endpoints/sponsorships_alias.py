from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import require_entrepreneur
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.sponsorship import SponsorshipRequest, SponsorshipRequestStatus
from app.schemas.sponsorship_request import (
    SponsorshipRequestRead, SponsorshipRequestSenderRead,
    SponsorshipRequestRecipientRead, SponsorshipRequestProjectRead,
)
from app.services.notification_service import NotificationService

router = APIRouter()

class SponsorshipRequestAliasCreate(BaseModel):
    sponsor_id: Optional[int] = None
    proposed_amount: Optional[float] = None
    proposal_message: Optional[str] = None
    deliverables: Optional[List[Any]] = None
    project_id: Optional[int] = None
    recipient_id: Optional[int] = None
    requested_amount: Optional[float] = None
    message: Optional[str] = None
    currency: str = "INR"
    sponsorship_type: str = "Financial Funding"

def _serialize_request(req):
    sender_read = None
    if req.sender:
        sender_read = SponsorshipRequestSenderRead(id=req.sender.id, full_name=req.sender.full_name, email=req.sender.email, avatar_url=req.sender.avatar_url)
    recipient_read = None
    if req.recipient:
        org_name = req.recipient.sponsor_profile.organization_name if req.recipient.sponsor_profile else None
        recipient_read = SponsorshipRequestRecipientRead(id=req.recipient.id, full_name=req.recipient.full_name, organization_name=org_name, avatar_url=req.recipient.avatar_url)
    project_read = None
    if req.project:
        project_read = SponsorshipRequestProjectRead(id=req.project.id, title=req.project.title, slug=req.project.slug, tagline=req.project.tagline, category=req.project.category, currency=req.project.currency)
    return SponsorshipRequestRead(id=req.id, sender_id=req.sender_id, recipient_id=req.recipient_id, project_id=req.project_id, message=req.message, requested_amount=req.requested_amount, currency=req.currency or "INR", sponsorship_type=req.sponsorship_type, requested_resources=req.requested_resources, response_note=req.response_note, status=req.status.value, created_at=req.created_at, updated_at=req.updated_at, sender=sender_read, recipient=recipient_read, project=project_read, commitment_id=req.commitment.id if req.commitment else None)

@router.post("/requests", response_model=SponsorshipRequestRead, status_code=status.HTTP_201_CREATED, summary="Create Sponsorship Request (Compatibility Alias)")
async def create_sponsorship_request_alias(data: SponsorshipRequestAliasCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_entrepreneur)):
    if not current_user.entrepreneur_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entrepreneur profile not found.")
    recipient_id = data.recipient_id or data.sponsor_id
    requested_amount = data.requested_amount or data.proposed_amount
    message = data.message or data.proposal_message or "Sponsorship request"
    if not recipient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sponsor_id or recipient_id is required.")
    if not data.project_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="project_id is required.")
    requested_resources = None
    if data.deliverables:
        requested_resources = "; ".join(str(d) for d in data.deliverables)
    proj_q = select(Project).where(Project.id == data.project_id, Project.entrepreneur_id == current_user.entrepreneur_profile.id)
    proj_res = await db.execute(proj_q)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or you are not authorized.")
    recipient_q = select(User).where(User.id == recipient_id).options(selectinload(User.sponsor_profile))
    rec_res = await db.execute(recipient_q)
    recipient = rec_res.scalar_one_or_none()
    if not recipient or recipient.role != UserRole.SPONSOR:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target sponsor user not found.")
    dup_q = select(SponsorshipRequest).where(SponsorshipRequest.project_id == data.project_id, SponsorshipRequest.recipient_id == recipient_id, SponsorshipRequest.status == SponsorshipRequestStatus.PENDING)
    dup_res = await db.execute(dup_q)
    if dup_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A pending sponsorship request already exists for this project and sponsor.")
    req = SponsorshipRequest(sender_id=current_user.id, recipient_id=recipient_id, project_id=data.project_id, message=message.strip(), requested_amount=requested_amount, currency=data.currency or "INR", sponsorship_type=data.sponsorship_type, requested_resources=requested_resources, status=SponsorshipRequestStatus.PENDING)
    db.add(req)
    await db.commit()
    await db.refresh(req)
    await NotificationService.create_notification(db=db, user_id=recipient_id, title=f"New Sponsorship Request: {project.title}", content=f"{current_user.full_name} submitted a sponsorship proposal for {project.title}.", type="sponsorship_request", entity_type="sponsorship_request", entity_id=req.id, link="/dashboard/sponsor")
    load_q = select(SponsorshipRequest).where(SponsorshipRequest.id == req.id).options(selectinload(SponsorshipRequest.sender), selectinload(SponsorshipRequest.recipient).selectinload(User.sponsor_profile), selectinload(SponsorshipRequest.project), selectinload(SponsorshipRequest.commitment))
    res = await db.execute(load_q)
    loaded_req = res.scalar_one()
    return _serialize_request(loaded_req)
