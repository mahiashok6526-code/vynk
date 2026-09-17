from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Stats ---
class AdminUsersStats(BaseSchema):
    total: int = 0
    entrepreneurs: int = 0
    sponsors: int = 0
    administrators: int = 0
    verified: int = 0
    unverified: int = 0
    suspended: int = 0


class AdminProjectsStats(BaseSchema):
    total: int = 0
    published: int = 0
    draft: int = 0
    archived: int = 0
    pending_moderation: int = 0
    approved: int = 0
    rejected: int = 0


class AdminSponsorshipStats(BaseSchema):
    total_requests: int = 0
    pending_requests: int = 0
    total_commitments: int = 0
    active_commitments: int = 0
    completed_commitments: int = 0
    cancelled_commitments: int = 0
    total_committed_funding: float = 0.0


class AdminPlatformStats(BaseSchema):
    average_trust_score: float = 50.0
    verified_users_count: int = 0
    open_reports_count: int = 0
    open_disputes_count: int = 0


class AdminDashboardResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    users: AdminUsersStats
    projects: AdminProjectsStats
    sponsorship: AdminSponsorshipStats
    sponsorships: Optional[Dict[str, Any]] = None
    platform: AdminPlatformStats
    trust: Optional[Dict[str, Any]] = None
    queues: Optional[Dict[str, Any]] = None
    recent_activity: List[Dict[str, Any]] = []
    recent_audit_logs: Optional[List[Dict[str, Any]]] = None


# --- User Management ---
class AdminUserItem(BaseSchema):
    id: int
    email: str
    username: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    is_suspended: bool = False
    suspended_at: Optional[datetime] = None
    suspended_by: Optional[int] = None
    suspension_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    trust_score: Optional[int] = 50


class AdminUserListResponse(BaseSchema):
    items: List[AdminUserItem]
    total: int
    page: int
    limit: int
    pages: int


class AdminUserDetail(AdminUserItem):
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    verification_records: List[Dict[str, Any]] = []
    projects_count: int = 0
    commitments_count: int = 0


class UserVerifyRequest(BaseModel):
    verification_type: str = "identity"  # identity, business_registration, accredited_investor
    notes: Optional[str] = None


class UserSuspendRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000)


# --- Project Moderation ---
class AdminProjectItem(BaseSchema):
    id: int
    title: str
    slug: str
    tagline: str
    category: str
    stage: str
    status: str
    moderation_status: str = "approved"
    moderation_reason: Optional[str] = None
    moderated_at: Optional[datetime] = None
    moderated_by: Optional[int] = None
    funding_goal: float = 0.0
    currency: str = "INR"
    entrepreneur_id: int
    entrepreneur_name: Optional[str] = None
    created_at: Optional[datetime] = None


class AdminProjectListResponse(BaseSchema):
    items: List[AdminProjectItem]
    total: int
    page: int
    limit: int
    pages: int


class ProjectModerateRequest(BaseModel):
    moderation_status: Optional[str] = None  # approved, rejected
    reason: Optional[str] = None


# --- Reports ---
class ReportCreateRequest(BaseModel):
    reported_user_id: Optional[int] = None
    reported_project_id: Optional[int] = None
    reported_sponsorship_request_id: Optional[int] = None
    reported_commitment_id: Optional[int] = None
    category: str = "other"  # spam, fraud, abuse, inappropriate_content, misrepresentation, other
    reason: Optional[str] = None
    description: Optional[str] = None
    details: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any):
        if isinstance(data, dict):
            if not data.get("reason") and data.get("description"):
                data["reason"] = data["description"][:255]
            elif not data.get("description") and data.get("reason"):
                data["description"] = data["reason"]
            if not data.get("reason"):
                data["reason"] = "General platform report"
        return data


class ReportResponse(BaseSchema):
    id: int
    reporter_id: int
    reporter_name: Optional[str] = None
    reported_user_id: Optional[int] = None
    reported_user_name: Optional[str] = None
    reported_project_id: Optional[int] = None
    reported_project_title: Optional[str] = None
    category: str
    reason: str
    details: Optional[str] = None
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class ReportListResponse(BaseSchema):
    items: List[ReportResponse]
    total: int
    page: int
    limit: int
    pages: int


class ReportResolveRequest(BaseModel):
    status: Optional[str] = "resolved"
    resolution_note: Optional[str] = "Resolved by administration"


# --- Disputes ---
class DisputeCreateRequest(BaseModel):
    commitment_id: Optional[int] = None
    request_id: Optional[int] = None
    sponsorship_request_id: Optional[int] = None
    reason: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=5000)

    @model_validator(mode="before")
    @classmethod
    def check_request_alias(cls, data: Any):
        if isinstance(data, dict):
            if not data.get("request_id") and data.get("sponsorship_request_id"):
                data["request_id"] = data["sponsorship_request_id"]
        return data


class DisputeResponse(BaseSchema):
    id: int
    commitment_id: Optional[int] = None
    request_id: Optional[int] = None
    initiator_id: int
    initiator_name: Optional[str] = None
    respondent_id: int
    respondent_name: Optional[str] = None
    reason: str
    description: str
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DisputeListResponse(BaseSchema):
    items: List[DisputeResponse]
    total: int
    page: int
    limit: int
    pages: int


class DisputeReviewRequest(BaseModel):
    """Payload for the /review endpoint — supports both under_review and resolved transitions."""
    status: Optional[str] = "under_review"  # under_review | resolved
    resolution_note: Optional[str] = None


class DisputeResolveRequest(BaseModel):
    resolution: str = Field(..., min_length=2, max_length=2000)

# Serialization map: internal DisputeStatus.OPEN ('open') → external API value ('opened')
# Use this in any endpoint that returns dispute status strings.
DISPUTE_STATUS_EXTERNAL = {
    "open": "opened",
    "under_review": "under_review",
    "resolved": "resolved",
    "dismissed": "dismissed",
}


# --- Audit Logs ---
class AdminAuditLogItem(BaseSchema):
    id: int
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    metadata_json: Dict[str, Any] = {}
    created_at: datetime


class AdminAuditLogListResponse(BaseSchema):
    items: List[AdminAuditLogItem]
    total: int
    page: int
    limit: int
    pages: int
