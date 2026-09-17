from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserRole, EntrepreneurProfile, SponsorProfile
from app.models.project import Project, ProjectStatus
from app.models.sponsorship import SponsorshipRequest, SponsorshipCommitment, CommitmentStatus
from app.models.trust import TrustScore, TrustScoreEvent
from app.models.moderation import (
    VerificationRecord,
    VerificationStatus,
    Report,
    ReportStatus,
    ReportCategory,
    Dispute,
    DisputeStatus,
    DisputeReason,
    AdminAuditLog,
)
from app.services.trust_service import TrustService
from app.services.notification_service import NotificationService


# External API status representation for disputes.
# The internal DisputeStatus.OPEN = "open" but the verify contract expects "opened".
_DISPUTE_STATUS_EXT: Dict[str, str] = {
    "open": "opened",
    "under_review": "under_review",
    "resolved": "resolved",
    "dismissed": "dismissed",
}


def _dispute_ext_status(dispute_status) -> str:
    """Translate internal DisputeStatus to external API status string."""
    raw = dispute_status.value if hasattr(dispute_status, "value") else str(dispute_status)
    return _DISPUTE_STATUS_EXT.get(raw, raw)


class AdminService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        admin_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[int],
        description: str,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> AdminAuditLog:
        """Create an immutable administrative audit log entry."""
        log_entry = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            metadata_json=metadata_json or {},
            created_at=datetime.now(timezone.utc),
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> Dict[str, Any]:
        """Compute live platform statistics from database records."""
        # 1. Users
        total_users = await db.scalar(select(func.count(User.id))) or 0
        entrepreneurs = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.ENTREPRENEUR)) or 0
        sponsors = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.SPONSOR)) or 0
        administrators = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.ADMIN)) or 0
        verified_users = await db.scalar(select(func.count(User.id)).where(User.is_verified.is_(True))) or 0
        unverified_users = total_users - verified_users
        suspended_users = await db.scalar(select(func.count(User.id)).where(User.is_suspended.is_(True))) or 0

        # 2. Projects
        total_projects = await db.scalar(select(func.count(Project.id))) or 0
        published_projects = await db.scalar(
            select(func.count(Project.id)).where(
                Project.status.in_([ProjectStatus.PUBLISHED, ProjectStatus.SEEKING_SPONSORSHIP, ProjectStatus.ACTIVE])
            )
        ) or 0
        draft_projects = await db.scalar(select(func.count(Project.id)).where(Project.status == ProjectStatus.DRAFT)) or 0
        archived_projects = await db.scalar(select(func.count(Project.id)).where(Project.status == ProjectStatus.ARCHIVED)) or 0
        pending_moderation = await db.scalar(select(func.count(Project.id)).where(Project.moderation_status == "pending_review")) or 0
        approved_projects = await db.scalar(select(func.count(Project.id)).where(Project.moderation_status == "approved")) or 0
        rejected_projects = await db.scalar(select(func.count(Project.id)).where(Project.moderation_status == "rejected")) or 0

        # 3. Sponsorships
        total_requests = await db.scalar(select(func.count(SponsorshipRequest.id))) or 0
        pending_requests = await db.scalar(select(func.count(SponsorshipRequest.id)).where(SponsorshipRequest.status == "pending")) or 0
        total_commitments = await db.scalar(select(func.count(SponsorshipCommitment.id))) or 0
        active_commitments = await db.scalar(
            select(func.count(SponsorshipCommitment.id)).where(
                SponsorshipCommitment.status.notin_([CommitmentStatus.COMPLETED, CommitmentStatus.CANCELLED])
            )
        ) or 0
        completed_commitments = await db.scalar(
            select(func.count(SponsorshipCommitment.id)).where(SponsorshipCommitment.status == CommitmentStatus.COMPLETED)
        ) or 0
        cancelled_commitments = await db.scalar(
            select(func.count(SponsorshipCommitment.id)).where(SponsorshipCommitment.status == CommitmentStatus.CANCELLED)
        ) or 0
        total_funding = await db.scalar(select(func.sum(SponsorshipCommitment.amount))) or 0.0

        # 4. Platform & Trust
        avg_trust = await db.scalar(select(func.avg(TrustScore.score))) or 50.0
        open_reports = await db.scalar(
            select(func.count(Report.id)).where(Report.status.in_([ReportStatus.PENDING, ReportStatus.OPEN, ReportStatus.INVESTIGATING, ReportStatus.UNDER_REVIEW]))
        ) or 0
        open_disputes = await db.scalar(
            select(func.count(Dispute.id)).where(Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW]))
        ) or 0

        # 5. Recent Activity
        recent_logs_q = (
            select(AdminAuditLog)
            .options(selectinload(AdminAuditLog.admin))
            .order_by(desc(AdminAuditLog.created_at))
            .limit(10)
        )
        recent_logs_res = await db.execute(recent_logs_q)
        recent_logs = recent_logs_res.scalars().all()

        activity = [
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "admin_name": log.admin.full_name if log.admin else "System",
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in recent_logs
        ]

        return {
            "users": {
                "total": total_users,
                "entrepreneurs": entrepreneurs,
                "sponsors": sponsors,
                "administrators": administrators,
                "verified": verified_users,
                "unverified": unverified_users,
                "suspended": suspended_users,
            },
            "projects": {
                "total": total_projects,
                "published": published_projects,
                "draft": draft_projects,
                "archived": archived_projects,
                "pending_moderation": pending_moderation,
                "approved": approved_projects,
                "rejected": rejected_projects,
            },
            "sponsorship": {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "total_commitments": total_commitments,
                "active_commitments": active_commitments,
                "completed_commitments": completed_commitments,
                "cancelled_commitments": cancelled_commitments,
                "total_committed_funding": float(total_funding),
            },
            "sponsorships": {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "total_commitments": total_commitments,
                "active": active_commitments,
                "completed": completed_commitments,
                "cancelled": cancelled_commitments,
                "disputed": open_disputes,
                "total_volume_usd": float(total_funding),
            },
            "platform": {
                "average_trust_score": round(float(avg_trust), 1),
                "verified_users_count": verified_users,
                "open_reports_count": open_reports,
                "open_disputes_count": open_disputes,
            },
            "trust": {
                "average_trust_score": round(float(avg_trust), 1),
                "highest_trust_score": round(float(await db.scalar(select(func.max(TrustScore.score))) or 50.0), 1),
                "lowest_trust_score": round(float(await db.scalar(select(func.min(TrustScore.score))) or 50.0), 1),
                "verified_users_count": verified_users,
            },
            "queues": {
                "pending_verifications": unverified_users,
                "pending_projects": pending_moderation,
                "pending_reports": open_reports,
                "open_disputes": open_disputes,
            },
            "recent_activity": activity,
            "recent_audit_logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "details": log.details,
                    "admin_id": log.admin_id,
                    "admin": {"full_name": log.admin.full_name, "email": log.admin.email} if log.admin else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in recent_logs
            ],
        }

    # ================= User Management =================
    @staticmethod
    async def list_users(
        db: AsyncSession,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_verified: Optional[bool] = None,
        is_suspended: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = select(User).options(selectinload(User.trust_score))
        conditions = []

        if search:
            s_term = f"%{search.strip()}%"
            conditions.append(or_(User.full_name.ilike(s_term), User.email.ilike(s_term), User.username.ilike(s_term)))
        if role:
            conditions.append(User.role == role)
        if is_verified is not None:
            conditions.append(User.is_verified.is_(is_verified))
        if is_suspended is not None:
            conditions.append(User.is_suspended.is_(is_suspended))

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(User.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))
        total = await db.scalar(count_q) or 0

        offset = (page - 1) * limit
        query = query.order_by(desc(User.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        users = res.scalars().all()

        user_items = []
        for u in users:
            ts_score = u.trust_score.score if u.trust_score else 50
            user_items.append({
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "full_name": u.full_name,
                "role": u.role.value if hasattr(u.role, "value") else str(u.role),
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "is_suspended": bool(u.is_suspended),
                "suspended_at": u.suspended_at,
                "suspended_by": u.suspended_by,
                "suspension_reason": u.suspension_reason,
                "created_at": u.created_at,
                "trust_score": ts_score,
            })

        return user_items, total

    @staticmethod
    async def get_user_detail(db: AsyncSession, user_id: int) -> Dict[str, Any]:
        query = select(User).where(User.id == user_id).options(
            selectinload(User.trust_score),
            selectinload(User.verification_records),
            selectinload(User.entrepreneur_profile),
            selectinload(User.sponsor_profile),
        )
        res = await db.execute(query)
        u = res.scalar_one_or_none()
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        projects_count = 0
        if u.entrepreneur_profile:
            projects_count = await db.scalar(select(func.count(Project.id)).where(Project.entrepreneur_id == u.entrepreneur_profile.id)) or 0

        commitments_count = 0
        if u.role == UserRole.SPONSOR and u.sponsor_profile:
            commitments_count = await db.scalar(select(func.count(SponsorshipCommitment.id)).where(SponsorshipCommitment.sponsor_id == u.sponsor_profile.id)) or 0
        elif u.role == UserRole.ENTREPRENEUR and u.entrepreneur_profile:
            commitments_count = await db.scalar(select(func.count(SponsorshipCommitment.id)).where(SponsorshipCommitment.entrepreneur_id == u.entrepreneur_profile.id)) or 0

        v_records = [
            {
                "id": vr.id,
                "verification_type": vr.verification_type,
                "status": vr.status.value if hasattr(vr.status, "value") else str(vr.status),
                "notes": vr.notes,
                "created_at": vr.created_at.isoformat() if vr.created_at else None,
                "reviewed_at": vr.reviewed_at.isoformat() if vr.reviewed_at else None,
            }
            for vr in (u.verification_records or [])
        ]

        return {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "is_suspended": bool(u.is_suspended),
            "suspended_at": u.suspended_at,
            "suspended_by": u.suspended_by,
            "suspension_reason": u.suspension_reason,
            "avatar_url": u.avatar_url,
            "headline": u.headline,
            "bio": u.bio,
            "location": u.location,
            "created_at": u.created_at,
            "trust_score": u.trust_score.score if u.trust_score else 50,
            "verification_records": v_records,
            "projects_count": projects_count,
            "commitments_count": commitments_count,
        }

    @staticmethod
    async def verify_user(
        db: AsyncSession,
        admin_id: int,
        user_id: int,
        verification_type: str = "identity",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        u = await db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        u.is_verified = True

        vr = VerificationRecord(
            user_id=user_id,
            verification_type=verification_type,
            status=VerificationStatus.APPROVED,
            notes=notes,
            reviewed_by=admin_id,
            reviewed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.add(vr)
        await db.commit()

        # Recalculate Trust Score using the existing deterministic Phase 7 calculation
        new_ts = await TrustService.recalculate_trust_score(db, user_id)

        # Notify user
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Profile Verified",
            content="Your Vynk account verification has been approved by the administrative team.",
            type="trust_score",
            link="/profile",
            entity_type="user",
            entity_id=user_id,
        )

        # Record immutable audit log
        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="verify_user",
            entity_type="user",
            entity_id=user_id,
            description=f"Verified user {u.email} ({u.full_name}) for type '{verification_type}'",
            metadata_json={"verification_type": verification_type, "notes": notes, "resulting_trust_score": new_ts.score},
        )

        return {"user_id": user_id, "is_verified": True, "trust_score": new_ts.score}

    @staticmethod
    async def revoke_verification(
        db: AsyncSession,
        admin_id: int,
        user_id: int,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        u = await db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        u.is_verified = False

        vr = VerificationRecord(
            user_id=user_id,
            verification_type="revocation",
            status=VerificationStatus.REJECTED,
            notes=reason,
            reviewed_by=admin_id,
            reviewed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.add(vr)
        await db.commit()

        new_ts = await TrustService.recalculate_trust_score(db, user_id)

        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Verification Revoked",
            content=f"Your verified badge has been revoked: {reason or 'Administrative review'}",
            type="trust_score",
            link="/profile",
            entity_type="user",
            entity_id=user_id,
        )

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="revoke_verification",
            entity_type="user",
            entity_id=user_id,
            description=f"Revoked verification for user {u.email}. Reason: {reason or 'Unspecified'}",
            metadata_json={"reason": reason, "resulting_trust_score": new_ts.score},
        )

        return {"user_id": user_id, "is_verified": False, "trust_score": new_ts.score}

    @staticmethod
    async def suspend_user(
        db: AsyncSession,
        admin_id: int,
        user_id: int,
        reason: str,
    ) -> Dict[str, Any]:
        if admin_id == user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Administrators cannot suspend their own account.")

        u = await db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        u.is_suspended = True
        u.suspended_at = datetime.now(timezone.utc)
        u.suspended_by = admin_id
        u.suspension_reason = reason
        await db.commit()

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="suspend_user",
            entity_type="user",
            entity_id=user_id,
            description=f"Suspended user {u.email}. Reason: {reason}",
            metadata_json={"reason": reason},
        )

        return {"user_id": user_id, "is_suspended": True, "reason": reason}

    @staticmethod
    async def unsuspend_user(
        db: AsyncSession,
        admin_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        u = await db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        u.is_suspended = False
        u.suspended_at = None
        u.suspended_by = None
        u.suspension_reason = None
        await db.commit()

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="unsuspend_user",
            entity_type="user",
            entity_id=user_id,
            description=f"Unsuspended user {u.email}.",
        )

        return {"user_id": user_id, "is_suspended": False}

    # ================= Project Moderation =================
    @staticmethod
    async def list_projects(
        db: AsyncSession,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        category: Optional[str] = None,
        moderation_status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = select(Project).options(selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user))
        conditions = []

        if search:
            s_term = f"%{search.strip()}%"
            conditions.append(or_(Project.title.ilike(s_term), Project.tagline.ilike(s_term)))
        if status_filter:
            conditions.append(Project.status == status_filter)
        if category:
            conditions.append(Project.category == category)
        if moderation_status:
            conditions.append(Project.moderation_status == moderation_status)

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(Project.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))
        total = await db.scalar(count_q) or 0

        offset = (page - 1) * limit
        query = query.order_by(desc(Project.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        projects = res.scalars().all()

        items = []
        for p in projects:
            e_name = p.entrepreneur.user.full_name if p.entrepreneur and p.entrepreneur.user else None
            items.append({
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "tagline": p.tagline,
                "category": p.category,
                "stage": p.stage.value if hasattr(p.stage, "value") else str(p.stage),
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "moderation_status": p.moderation_status,
                "moderation_reason": p.moderation_reason,
                "moderated_at": p.moderated_at,
                "moderated_by": p.moderated_by,
                "funding_goal": p.funding_goal,
                "currency": p.currency,
                "entrepreneur_id": p.entrepreneur_id,
                "entrepreneur_name": e_name,
                "created_at": p.created_at,
            })

        return items, total

    @staticmethod
    async def get_project_detail(db: AsyncSession, project_id: int) -> Dict[str, Any]:
        query = select(Project).where(Project.id == project_id).options(
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user),
            selectinload(Project.requirements),
        )
        res = await db.execute(query)
        p = res.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        e_name = p.entrepreneur.user.full_name if p.entrepreneur and p.entrepreneur.user else None
        e_email = p.entrepreneur.user.email if p.entrepreneur and p.entrepreneur.user else None

        return {
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "tagline": p.tagline,
            "description": p.description,
            "category": p.category,
            "stage": p.stage.value if hasattr(p.stage, "value") else str(p.stage),
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
            "moderation_status": p.moderation_status,
            "moderation_reason": p.moderation_reason,
            "moderated_at": p.moderated_at,
            "moderated_by": p.moderated_by,
            "funding_goal": p.funding_goal,
            "funding_received": p.funding_received,
            "currency": p.currency,
            "entrepreneur_id": p.entrepreneur_id,
            "entrepreneur_name": e_name,
            "entrepreneur_email": e_email,
            "created_at": p.created_at,
        }

    @staticmethod
    async def approve_project(
        db: AsyncSession,
        admin_id: int,
        project_id: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        p_q = select(Project).where(Project.id == project_id).options(
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user)
        )
        res = await db.execute(p_q)
        p = res.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        p.moderation_status = "approved"
        p.moderation_reason = notes
        p.moderated_at = datetime.now(timezone.utc)
        p.moderated_by = admin_id
        await db.commit()

        # Notify entrepreneur
        if p.entrepreneur and p.entrepreneur.user:
            await NotificationService.create_notification(
                db=db,
                user_id=p.entrepreneur.user.id,
                title="Project Approved",
                content=f"Your project showcase '{p.title}' has been reviewed and approved by moderators.",
                type="commitment",
                link=f"/projects/{p.id}",
                entity_type="project",
                entity_id=p.id,
            )

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="approve_project",
            entity_type="project",
            entity_id=p.id,
            description=f"Approved project #{p.id} ('{p.title}')",
            metadata_json={"notes": notes},
        )

        return {"project_id": p.id, "moderation_status": "approved"}

    @staticmethod
    async def reject_project(
        db: AsyncSession,
        admin_id: int,
        project_id: int,
        reason: str,
    ) -> Dict[str, Any]:
        p_q = select(Project).where(Project.id == project_id).options(
            selectinload(Project.entrepreneur).selectinload(EntrepreneurProfile.user)
        )
        res = await db.execute(p_q)
        p = res.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        p.moderation_status = "rejected"
        p.moderation_reason = reason
        p.moderated_at = datetime.now(timezone.utc)
        p.moderated_by = admin_id
        await db.commit()

        if p.entrepreneur and p.entrepreneur.user:
            await NotificationService.create_notification(
                db=db,
                user_id=p.entrepreneur.user.id,
                title="Project Moderation Update",
                content=f"Your project showcase '{p.title}' requires revision: {reason}",
                type="commitment",
                link=f"/projects/{p.id}/edit",
                entity_type="project",
                entity_id=p.id,
            )

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="reject_project",
            entity_type="project",
            entity_id=p.id,
            description=f"Rejected project #{p.id} ('{p.title}'). Reason: {reason}",
            metadata_json={"reason": reason},
        )

        return {
            "project_id": p.id,
            "moderation_status": "rejected",
            "moderation_reason": reason,
            "reason": reason,
        }

    # ================= Reporting System =================
    @staticmethod
    async def create_report(
        db: AsyncSession,
        reporter_id: int,
        reported_user_id: Optional[int] = None,
        reported_project_id: Optional[int] = None,
        reported_sponsorship_request_id: Optional[int] = None,
        reported_commitment_id: Optional[int] = None,
        category: str = "other",
        reason: str = "",
        details: Optional[str] = None,
    ) -> Report:
        if not any([reported_user_id, reported_project_id, reported_sponsorship_request_id, reported_commitment_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A report must specify at least one target entity (user, project, request, or commitment).",
            )

        if reported_user_id and reported_user_id == reporter_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot submit a report against your own account.",
            )

        # Validate existence of targets
        if reported_user_id:
            target_user = await db.get(User, reported_user_id)
            if not target_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reported user not found.")
        if reported_project_id:
            target_project = await db.get(Project, reported_project_id)
            if not target_project:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reported project not found.")

        report = Report(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reported_project_id=reported_project_id,
            reported_sponsorship_request_id=reported_sponsorship_request_id,
            reported_commitment_id=reported_commitment_id,
            category=category,
            reason=reason,
            details=details,
            status=ReportStatus.OPEN,
            created_at=datetime.now(timezone.utc),
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    @staticmethod
    async def list_reports(
        db: AsyncSession,
        status_filter: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = select(Report).options(
            selectinload(Report.reporter),
            selectinload(Report.reported_user),
            selectinload(Report.reported_project),
            selectinload(Report.reviewer),
        )
        conditions = []

        if status_filter:
            conditions.append(Report.status == status_filter)
        if category:
            conditions.append(Report.category == category)

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(Report.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))
        total = await db.scalar(count_q) or 0

        offset = (page - 1) * limit
        query = query.order_by(desc(Report.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        reports = res.scalars().all()

        items = []
        for r in reports:
            items.append({
                "id": r.id,
                "reporter_id": r.reporter_id,
                "reporter_name": r.reporter.full_name if r.reporter else None,
                "reported_user_id": r.reported_user_id,
                "reported_user_name": r.reported_user.full_name if r.reported_user else None,
                "reported_project_id": r.reported_project_id,
                "reported_project_title": r.reported_project.title if r.reported_project else None,
                "category": r.category,
                "reason": r.reason,
                "details": r.details,
                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "reviewed_by": r.reviewed_by,
                "reviewed_at": r.reviewed_at,
                "resolution_note": r.resolution_note,
                "created_at": r.created_at,
                "resolved_at": r.resolved_at,
            })

        return items, total

    @staticmethod
    async def get_report_detail(db: AsyncSession, report_id: int) -> Dict[str, Any]:
        query = select(Report).where(Report.id == report_id).options(
            selectinload(Report.reporter),
            selectinload(Report.reported_user),
            selectinload(Report.reported_project),
            selectinload(Report.reviewer),
        )
        res = await db.execute(query)
        r = res.scalar_one_or_none()
        if not r:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        return {
            "id": r.id,
            "reporter_id": r.reporter_id,
            "reporter_name": r.reporter.full_name if r.reporter else None,
            "reported_user_id": r.reported_user_id,
            "reported_user_name": r.reported_user.full_name if r.reported_user else None,
            "reported_project_id": r.reported_project_id,
            "reported_project_title": r.reported_project.title if r.reported_project else None,
            "category": r.category,
            "reason": r.reason,
            "details": r.details,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "reviewed_by": r.reviewed_by,
            "reviewed_at": r.reviewed_at,
            "resolution_note": r.resolution_note,
            "created_at": r.created_at,
            "resolved_at": r.resolved_at,
        }

    @staticmethod
    async def review_report(
        db: AsyncSession,
        admin_id: int,
        report_id: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        r = await db.get(Report, report_id)
        if not r:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        r.status = ReportStatus.UNDER_REVIEW
        r.reviewed_by = admin_id
        r.reviewed_at = datetime.now(timezone.utc)
        if notes:
            r.resolution_note = notes
        await db.commit()

        return {"report_id": report_id, "status": "under_review"}

    @staticmethod
    async def resolve_report(
        db: AsyncSession,
        admin_id: int,
        report_id: int,
        resolution_note: str,
    ) -> Dict[str, Any]:
        r = await db.get(Report, report_id)
        if not r:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        r.status = ReportStatus.RESOLVED
        r.reviewed_by = admin_id
        r.reviewed_at = datetime.now(timezone.utc)
        r.resolved_at = datetime.now(timezone.utc)
        r.resolution_note = resolution_note
        await db.commit()

        # Notify reporter
        await NotificationService.create_notification(
            db=db,
            user_id=r.reporter_id,
            title="Report Resolved",
            content=f"Your submitted report #{r.id} has been investigated and resolved.",
            type="system",
            link="/notifications",
            entity_type="report",
            entity_id=r.id,
        )

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="resolve_report",
            entity_type="report",
            entity_id=report_id,
            description=f"Resolved report #{report_id}. Resolution: {resolution_note}",
            metadata_json={"resolution_note": resolution_note},
        )

        return {"report_id": report_id, "status": "resolved", "resolution_note": resolution_note}

    @staticmethod
    async def dismiss_report(
        db: AsyncSession,
        admin_id: int,
        report_id: int,
        resolution_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        r = await db.get(Report, report_id)
        if not r:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        r.status = ReportStatus.DISMISSED
        r.reviewed_by = admin_id
        r.reviewed_at = datetime.now(timezone.utc)
        r.resolved_at = datetime.now(timezone.utc)
        r.resolution_note = resolution_note or "Dismissed by moderator."
        await db.commit()

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="dismiss_report",
            entity_type="report",
            entity_id=report_id,
            description=f"Dismissed report #{report_id}.",
            metadata_json={"resolution_note": resolution_note},
        )

        return {"report_id": report_id, "status": "dismissed"}

    # ================= Dispute Management =================
    @staticmethod
    async def create_dispute(
        db: AsyncSession,
        initiator_id: int,
        commitment_id: Optional[int] = None,
        request_id: Optional[int] = None,
        reason: str = "commitment_disagreement",
        description: str = "",
    ) -> Dispute:
        if not commitment_id and not request_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A dispute must be linked to either a commitment or a sponsorship request.",
            )

        respondent_id: Optional[int] = None

        if commitment_id:
            comm_q = select(SponsorshipCommitment).where(SponsorshipCommitment.id == commitment_id).options(
                selectinload(SponsorshipCommitment.sponsor),
                selectinload(SponsorshipCommitment.entrepreneur),
            )
            comm_res = await db.execute(comm_q)
            comm = comm_res.scalar_one_or_none()
            if not comm:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship commitment not found.")

            sponsor_user_id = comm.sponsor.user_id if comm.sponsor else None
            entrepreneur_user_id = comm.entrepreneur.user_id if comm.entrepreneur else None

            if initiator_id == sponsor_user_id:
                respondent_id = entrepreneur_user_id
            elif initiator_id == entrepreneur_user_id:
                respondent_id = sponsor_user_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not an authorized party to this sponsorship commitment.",
                )

        elif request_id:
            req_q = select(SponsorshipRequest).where(SponsorshipRequest.id == request_id)
            req_res = await db.execute(req_q)
            req = req_res.scalar_one_or_none()
            if not req:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsorship request not found.")

            if initiator_id == req.sender_id:
                respondent_id = req.recipient_id
            elif initiator_id == req.recipient_id:
                respondent_id = req.sender_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not an authorized party to this sponsorship request.",
                )

        if not respondent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine counterparty respondent for this dispute.",
            )

        dispute = Dispute(
            commitment_id=commitment_id,
            request_id=request_id,
            initiator_id=initiator_id,
            respondent_id=respondent_id,
            reason=reason,
            description=description,
            status=DisputeStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(dispute)
        await db.commit()
        await db.refresh(dispute)

        # Notify respondent
        await NotificationService.create_notification(
            db=db,
            user_id=respondent_id,
            title="Dispute Initiated",
            content=f"A sponsorship dispute (#{dispute.id}) has been opened regarding your recent engagement.",
            type="commitment",
            link="/notifications",
            entity_type="dispute",
            entity_id=dispute.id,
        )

        return dispute

    @staticmethod
    async def list_disputes(
        db: AsyncSession,
        status_filter: Optional[str] = None,
        reason: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = select(Dispute).options(
            selectinload(Dispute.initiator),
            selectinload(Dispute.respondent),
            selectinload(Dispute.reviewer),
        )
        conditions = []

        if status_filter:
            conditions.append(Dispute.status == status_filter)
        if reason:
            conditions.append(Dispute.reason == reason)

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(Dispute.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))
        total = await db.scalar(count_q) or 0

        offset = (page - 1) * limit
        query = query.order_by(desc(Dispute.created_at)).offset(offset).limit(limit)
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

        return items, total

    @staticmethod
    async def get_dispute_detail(db: AsyncSession, dispute_id: int) -> Dict[str, Any]:
        query = select(Dispute).where(Dispute.id == dispute_id).options(
            selectinload(Dispute.initiator),
            selectinload(Dispute.respondent),
            selectinload(Dispute.reviewer),
        )
        res = await db.execute(query)
        d = res.scalar_one_or_none()
        if not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

        return {
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
        }

    @staticmethod
    async def review_dispute(
        db: AsyncSession,
        admin_id: int,
        dispute_id: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        d = await db.get(Dispute, dispute_id)
        if not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

        d.status = DisputeStatus.UNDER_REVIEW
        d.reviewed_by = admin_id
        d.reviewed_at = datetime.now(timezone.utc)
        d.updated_at = datetime.now(timezone.utc)
        await db.commit()

        return {"dispute_id": dispute_id, "status": "under_review"}

    @staticmethod
    async def resolve_dispute(
        db: AsyncSession,
        admin_id: int,
        dispute_id: int,
        resolution: str,
    ) -> Dict[str, Any]:
        d = await db.get(Dispute, dispute_id)
        if not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

        d.status = DisputeStatus.RESOLVED
        d.reviewed_by = admin_id
        d.reviewed_at = datetime.now(timezone.utc)
        d.resolution = resolution
        d.updated_at = datetime.now(timezone.utc)
        await db.commit()

        # Notify both parties
        for uid in [d.initiator_id, d.respondent_id]:
            await NotificationService.create_notification(
                db=db,
                user_id=uid,
                title="Dispute Resolved",
                content=f"Dispute #{d.id} has been resolved by administrative mediation: {resolution}",
                type="commitment",
                link="/notifications",
                entity_type="dispute",
                entity_id=d.id,
            )

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="resolve_dispute",
            entity_type="dispute",
            entity_id=dispute_id,
            description=f"Resolved dispute #{dispute_id}. Resolution: {resolution}",
            metadata_json={"resolution": resolution},
        )

        return {"dispute_id": dispute_id, "status": "resolved", "resolution": resolution}

    @staticmethod
    async def dismiss_dispute(
        db: AsyncSession,
        admin_id: int,
        dispute_id: int,
        resolution: Optional[str] = None,
    ) -> Dict[str, Any]:
        d = await db.get(Dispute, dispute_id)
        if not d:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")

        d.status = DisputeStatus.DISMISSED
        d.reviewed_by = admin_id
        d.reviewed_at = datetime.now(timezone.utc)
        d.resolution = resolution or "Dismissed by administrative review."
        d.updated_at = datetime.now(timezone.utc)
        await db.commit()

        await AdminService.log_action(
            db=db,
            admin_id=admin_id,
            action="dismiss_dispute",
            entity_type="dispute",
            entity_id=dispute_id,
            description=f"Dismissed dispute #{dispute_id}.",
            metadata_json={"resolution": resolution},
        )

        return {"dispute_id": dispute_id, "status": "dismissed"}

    # ================= Audit Log Listing =================
    @staticmethod
    async def list_audit_logs(
        db: AsyncSession,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        admin_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = select(AdminAuditLog).options(selectinload(AdminAuditLog.admin))
        conditions = []

        if action:
            conditions.append(AdminAuditLog.action == action)
        if entity_type:
            conditions.append(AdminAuditLog.entity_type == entity_type)
        if admin_id:
            conditions.append(AdminAuditLog.admin_id == admin_id)

        if conditions:
            query = query.where(and_(*conditions))

        count_q = select(func.count(AdminAuditLog.id))
        if conditions:
            count_q = count_q.where(and_(*conditions))
        total = await db.scalar(count_q) or 0

        offset = (page - 1) * limit
        query = query.order_by(desc(AdminAuditLog.created_at)).offset(offset).limit(limit)
        res = await db.execute(query)
        logs = res.scalars().all()

        items = []
        for l in logs:
            items.append({
                "id": l.id,
                "admin_id": l.admin_id,
                "admin_name": l.admin.full_name if l.admin else "System",
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "description": l.description,
                "metadata_json": l.metadata_json or {},
                "created_at": l.created_at,
            })

        return items, total
