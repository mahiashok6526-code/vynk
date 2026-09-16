from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CommitmentUpdateRead(BaseModel):
    id: int
    updated_by: int
    previous_status: str
    new_status: str
    note: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CommitmentBase(BaseModel):
    project_id: int
    amount: float = Field(..., gt=0)
    sponsorship_type: str
    status: str = "interested"
    expected_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    agreement_reference: Optional[str] = None
    notes: Optional[str] = None


class CommitmentCreate(CommitmentBase):
    pass


class CommitmentStatusUpdate(BaseModel):
    new_status: str = Field(..., pattern="^(interested|discussion|promised|confirmed|agreement|funded|completed|cancelled)$")
    note: str = Field(..., min_length=1)
    follow_up_date: Optional[datetime] = None
    agreement_reference: Optional[str] = None


class CommitmentRead(CommitmentBase):
    id: int
    sponsor_id: int
    entrepreneur_id: int
    request_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    updates: List[CommitmentUpdateRead] = []

    model_config = {"from_attributes": True}
