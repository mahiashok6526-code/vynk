import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.services.admin_service import AdminService
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminUserListResponse,
    AdminUserDetail,
    UserVerifyRequest,
    UserSuspendRequest,
    AdminProjectListResponse,
    AdminProjectItem,
    ProjectModerateRequest,
    ReportListResponse,
    ReportResponse,
    ReportResolveRequest,
    DisputeListResponse,
    DisputeResponse,
    DisputeResolveRequest,
    DisputeReviewRequest,
    AdminAuditLogListResponse,
)

router = APIRouter()


# ================= Dashboard & Stats =================
@router.get("/dashboard", response_model=AdminDashboardResponse, summary="Admin Dashboard Statistics")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Retrieve comprehensive platform metrics across users, projects, sponsorships, and platform health."""
    return await AdminService.get_dashboard_stats(db)


@router.get("/stats", summary="Platform Statistics (Backward Compatible)")
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Admin-only summary of platform metrics and queues for backward compatibility."""
    stats = await AdminService.get_dashboard_stats(db)
    return {
        "users": {
            "total": stats["users"]["total"],
            "entrepreneurs": stats["users"]["entrepreneurs"],
            "sponsors": stats["users"]["sponsors"],
            "administrators": stats["users"]["administrators"],
        },
        "projects_count": stats["projects"]["total"],
        "commitments": {
            "total_count": stats["sponsorship"]["total_commitments"],
            "total_funding_usd": stats["sponsorship"]["total_committed_funding"],
        },
        "average_trust_score": stats["platform"]["average_trust_score"],
        "queue": {
            "pending_verifications": stats["users"]["unverified"],
            "pending_reports": stats["platform"]["open_reports_count"],
        },
    }


# ================= User Management =================
@router.get("/users", response_model=AdminUserListResponse, summary="List Users")
async def list_admin_users(
    search: Optional[str] = Query(None, description="Search by name, email, or username"),
    role: Optional[str] = Query(None, description="Filter by role: entrepreneur, sponsor, admin"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified badge"),
    is_suspended: Optional[bool] = Query(None, description="Filter by suspension status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    items, total = await AdminService.list_users(
        db, search=search, role=role, is_verified=is_verified, is_suspended=is_suspended, page=page, limit=limit
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


@router.get("/users/{user_id}", response_model=AdminUserDetail, summary="Get User Details")
async def get_admin_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.get_user_detail(db, user_id)


@router.post("/users/{user_id}/verify", summary="Verify User")
async def verify_user(
    user_id: int,
    payload: Optional[UserVerifyRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    v_type = payload.verification_type if payload else "identity"
    notes = payload.notes if payload else None
    return await AdminService.verify_user(db, admin_id=admin_user.id, user_id=user_id, verification_type=v_type, notes=notes)


@router.post("/users/{user_id}/revoke-verification", summary="Revoke User Verification")
async def revoke_user_verification(
    user_id: int,
    payload: Optional[UserVerifyRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    reason = payload.notes if payload else None
    return await AdminService.revoke_verification(db, admin_id=admin_user.id, user_id=user_id, reason=reason)


@router.post("/users/{user_id}/suspend", summary="Suspend User")
async def suspend_user(
    user_id: int,
    payload: UserSuspendRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.suspend_user(db, admin_id=admin_user.id, user_id=user_id, reason=payload.reason)


@router.post("/users/{user_id}/unsuspend", summary="Unsuspend User")
async def unsuspend_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.unsuspend_user(db, admin_id=admin_user.id, user_id=user_id)


# ================= Project Moderation =================
@router.get("/projects", response_model=AdminProjectListResponse, summary="List Projects for Moderation")
async def list_admin_projects(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    moderation_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    items, total = await AdminService.list_projects(
        db, search=search, status_filter=status, category=category, moderation_status=moderation_status, page=page, limit=limit
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


@router.get("/projects/{project_id}", summary="Get Project Details for Moderation")
async def get_admin_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.get_project_detail(db, project_id)


@router.post("/projects/{project_id}/approve", summary="Approve Project")
async def approve_project(
    project_id: int,
    payload: Optional[ProjectModerateRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    notes = payload.reason if payload else None
    return await AdminService.approve_project(db, admin_id=admin_user.id, project_id=project_id, notes=notes)


@router.post("/projects/{project_id}/reject", summary="Reject Project / Request Changes")
async def reject_project(
    project_id: int,
    payload: ProjectModerateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.reject_project(db, admin_id=admin_user.id, project_id=project_id, reason=payload.reason or "Does not meet guidelines.")


# ================= Report Moderation =================
@router.get("/reports", response_model=ReportListResponse, summary="List Reports")
async def list_admin_reports(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    items, total = await AdminService.list_reports(db, status_filter=status, category=category, page=page, limit=limit)
    pages = math.ceil(total / limit) if total > 0 else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


@router.get("/reports/{report_id}", response_model=ReportResponse, summary="Get Report Detail")
async def get_admin_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.get_report_detail(db, report_id)


@router.post("/reports/{report_id}/review", summary="Review or Resolve Report")
async def review_report(
    report_id: int,
    payload: Optional[ReportResolveRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Mark a report as under review. If payload contains status='resolved', resolves the report directly."""
    if payload and payload.status == "resolved":
        resolution_note = payload.resolution_note or "Resolved by administration"
        return await AdminService.resolve_report(
            db, admin_id=admin_user.id, report_id=report_id, resolution_note=resolution_note
        )
    notes = payload.resolution_note if payload else None
    return await AdminService.review_report(db, admin_id=admin_user.id, report_id=report_id, notes=notes)


@router.post("/reports/{report_id}/resolve", summary="Resolve Report")
async def resolve_report(
    report_id: int,
    payload: ReportResolveRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.resolve_report(db, admin_id=admin_user.id, report_id=report_id, resolution_note=payload.resolution_note)


@router.post("/reports/{report_id}/dismiss", summary="Dismiss Report")
async def dismiss_report(
    report_id: int,
    payload: Optional[ReportResolveRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    res_note = payload.resolution_note if payload else None
    return await AdminService.dismiss_report(db, admin_id=admin_user.id, report_id=report_id, resolution_note=res_note)


# ================= Dispute Moderation =================
@router.get("/disputes", response_model=DisputeListResponse, summary="List Disputes")
async def list_admin_disputes(
    status: Optional[str] = Query(None),
    reason: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    items, total = await AdminService.list_disputes(db, status_filter=status, reason=reason, page=page, limit=limit)
    pages = math.ceil(total / limit) if total > 0 else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


@router.get("/disputes/{dispute_id}", response_model=DisputeResponse, summary="Get Dispute Detail")
async def get_admin_dispute(
    dispute_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.get_dispute_detail(db, dispute_id)


@router.post("/disputes/{dispute_id}/review", summary="Review or Resolve Dispute")
async def review_dispute(
    dispute_id: int,
    payload: Optional[DisputeReviewRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    """Mark a dispute as under review. If payload contains status='resolved', resolves the dispute directly."""
    if payload and payload.status == "resolved":
        resolution = payload.resolution_note or "Resolved by administrative review."
        return await AdminService.resolve_dispute(
            db, admin_id=admin_user.id, dispute_id=dispute_id, resolution=resolution
        )
    notes = payload.resolution_note if payload else None
    return await AdminService.review_dispute(db, admin_id=admin_user.id, dispute_id=dispute_id, notes=notes)


@router.post("/disputes/{dispute_id}/resolve", summary="Resolve Dispute")
async def resolve_dispute(
    dispute_id: int,
    payload: DisputeResolveRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return await AdminService.resolve_dispute(db, admin_id=admin_user.id, dispute_id=dispute_id, resolution=payload.resolution)


@router.post("/disputes/{dispute_id}/dismiss", summary="Dismiss Dispute")
async def dismiss_dispute(
    dispute_id: int,
    payload: Optional[DisputeResolveRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    resolution = payload.resolution if payload else None
    return await AdminService.dismiss_dispute(db, admin_id=admin_user.id, dispute_id=dispute_id, resolution=resolution)


# ================= Audit Trail =================
@router.get("/audit-logs", response_model=AdminAuditLogListResponse, summary="List Admin Audit Logs")
async def list_admin_audit_logs(
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    admin_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    target_admin_id = admin_id if admin_id is not None else admin_user.id
    items, total = await AdminService.list_audit_logs(
        db, action=action, entity_type=entity_type, admin_id=target_admin_id, page=page, limit=limit
    )
    pages = math.ceil(total / limit) if total > 0 else 1
    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}

