from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SponsorshipRequestSenderRead(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class SponsorshipRequestRecipientRead(BaseModel):
    id: int
    full_name: str
    organization_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class SponsorshipRequestProjectRead(BaseModel):
    id: int
    title: str
    slug: str
    tagline: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = "INR"

    model_config = {"from_attributes": True}


class SponsorshipRequestBase(BaseModel):
    project_id: int
    recipient_id: int
    sponsorship_type: str = "Financial Funding"
    requested_amount: Optional[float] = Field(None, ge=0)
    currency: str = "INR"
    requested_resources: Optional[str] = None
    message: str = Field(..., min_length=5)


class SponsorshipRequestCreate(SponsorshipRequestBase):
    pass


class SponsorshipRequestRespond(BaseModel):
    action: str = Field(..., pattern="^(accept|reject)$")
    response_note: Optional[str] = None
    commitment_amount: Optional[float] = Field(None, ge=0)
    expected_date: Optional[datetime] = None


class SponsorshipRequestRead(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    project_id: int
    message: str
    requested_amount: Optional[float] = None
    currency: str = "INR"
    sponsorship_type: str
    requested_resources: Optional[str] = None
    response_note: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    sender: Optional[SponsorshipRequestSenderRead] = None
    recipient: Optional[SponsorshipRequestRecipientRead] = None
    project: Optional[SponsorshipRequestProjectRead] = None
    commitment_id: Optional[int] = None

    model_config = {"from_attributes": True}
