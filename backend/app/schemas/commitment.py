from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class CommitmentUpdateRead(BaseModel):
    id: int
    commitment_id: Optional[int] = None
    updated_by: int
    update_type: str = "status_change"
    title: Optional[str] = None
    previous_status: str
    new_status: str
    note: str
    evidence_reference: Optional[str] = None
    event_date: Optional[datetime] = None
    created_at: datetime
    updater_name: Optional[str] = None
    updater_role: Optional[str] = None

    model_config = {"from_attributes": True}


class CommitmentMilestoneCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    note: str = Field(..., min_length=2)
    update_type: str = Field(default="milestone", max_length=50)
    evidence_reference: Optional[str] = Field(None, max_length=512)
    event_date: Optional[datetime] = None


class CommitmentBase(BaseModel):
    project_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(default=0.0, ge=0)
    currency: str = "INR"
    sponsorship_type: str
    status: str = "interested"
    expected_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    follow_up_reason: Optional[str] = None
    agreement_reference: Optional[str] = None
    cancellation_type: Optional[str] = None
    notes: Optional[str] = None


class CommitmentCreate(CommitmentBase):
    request_id: Optional[int] = None


class CommitmentStatusUpdate(BaseModel):
    new_status: str = Field(..., pattern="^(interested|discussion|promised|confirmed|agreement|funded|completed|cancelled)$")
    note: str = Field(..., min_length=1)
    follow_up_date: Optional[datetime] = None
    follow_up_reason: Optional[str] = None
    agreement_reference: Optional[str] = None
    cancellation_type: Optional[str] = Field(None, pattern="^(mutual|unilateral)$")


class CommitmentRead(CommitmentBase):
    id: int
    sponsor_id: int
    entrepreneur_id: int
    request_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    updates: List[CommitmentUpdateRead] = []

    # Enriched context fields
    project_title: Optional[str] = None
    project_slug: Optional[str] = None
    sponsor_name: Optional[str] = None
    sponsor_org: Optional[str] = None
    sponsor_avatar: Optional[str] = None
    entrepreneur_name: Optional[str] = None
    entrepreneur_avatar: Optional[str] = None
    is_overdue: bool = False

    model_config = {"from_attributes": True}

