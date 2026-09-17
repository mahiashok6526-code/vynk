from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.moderation import Report, Dispute
from app.services.admin_service import AdminService, _dispute_ext_status
from app.schemas.admin import (
    ReportCreateRequest,
    ReportResponse,
    DisputeCreateRequest,
    DisputeResponse,
)

router = APIRouter()


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, summary="Submit a Report")
async def submit_report(
    payload: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Authenticated user submits a report regarding problematic content or behavior."""
    report = await AdminService.create_report(
        db=db,
        reporter_id=current_user.id,
        reported_user_id=payload.reported_user_id,
        reported_project_id=payload.reported_project_id,
        reported_sponsorship_request_id=payload.reported_sponsorship_request_id,
        reported_commitment_id=payload.reported_commitment_id,
        category=payload.category,
        reason=payload.reason,
        details=payload.details,
    )
    return await AdminService.get_report_detail(db, report.id)


@router.post("/disputes", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED, summary="Initiate a Dispute")
async def initiate_dispute(
    payload: DisputeCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Involved user opens a formal sponsorship disagreement or commitment dispute."""
    dispute = await AdminService.create_dispute(
        db=db,
        initiator_id=current_user.id,
        commitment_id=payload.commitment_id,
        request_id=payload.request_id,
        reason=payload.reason,
        description=payload.description,
    )
    return await AdminService.get_dispute_detail(db, dispute.id)


@router.get("/disputes/my", response_model=List[DisputeResponse], summary="List My Disputes")
async def get_my_disputes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all disputes where current user is initiator or respondent."""
    query = (
        select(Dispute)
        .where(or_(Dispute.initiator_id == current_user.id, Dispute.respondent_id == current_user.id))
        .options(
            selectinload(Dispute.initiator),
            selectinload(Dispute.respondent),
            selectinload(Dispute.reviewer),
        )
        .order_by(desc(Dispute.created_at))
    )
    res = await db.execute(query)
    disputes = res.scalars().all()

    items = []
    for d in disputes:
        items.append({
            "id": d.id,
            "commitment_id": d.commitment_id,
            "request_id": d.request_id,
            "initiator_id": d.initiator_id,
            "initiator_name": d.initiator.full_name if d.initiator else None,
            "respondent_id": d.respondent_id,
            "respondent_name": d.respondent.full_name if d.respondent else None,
            "reason": d.reason,
            "description": d.description,
            "status": _dispute_ext_status(d.status),
            "reviewed_by": d.reviewed_by,
            "reviewed_at": d.reviewed_at,
            "resolution": d.resolution,
            "created_at": d.created_at,
            "updated_at": d.updated_at,
        })
    return items
