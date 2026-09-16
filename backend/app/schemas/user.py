from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr


class EntrepreneurProfileRead(BaseModel):
    id: int
    user_id: int
    stage: str
    industry: Optional[str] = None
    skills: List[str] = []
    pitch_deck_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None

    model_config = {"from_attributes": True}


class SponsorProfileRead(BaseModel):
    id: int
    user_id: int
    organization_name: Optional[str] = None
    sponsor_type: str
    focus_industries: List[str] = []
    min_budget: int
    max_budget: int
    preferred_sponsorship_types: List[str] = []

    model_config = {"from_attributes": True}


class TrustScoreBrief(BaseModel):
    score: int
    verification_points: int
    commitments_points: int
    responsiveness_points: int
    activity_points: int
    completed_commitments_count: int

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    entrepreneur_profile: Optional[EntrepreneurProfileRead] = None
    sponsor_profile: Optional[SponsorProfileRead] = None
    trust_score: Optional[TrustScoreBrief] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
