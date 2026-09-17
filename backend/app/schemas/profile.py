from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    duration: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = ""


class EducationItem(BaseModel):
    institution: str = Field(..., min_length=1, max_length=150)
    degree: str = Field(..., min_length=1, max_length=100)
    year: str = Field(..., min_length=1, max_length=50)


class AchievementItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    year: Optional[str] = ""
    description: Optional[str] = ""


class CollaborationItem(BaseModel):
    partner_name: str = Field(..., min_length=1, max_length=150)
    year: Optional[str] = ""
    description: Optional[str] = ""
    outcome: Optional[str] = ""


class ProfileCompletionRead(BaseModel):
    percentage: int
    completed_fields: List[str]
    missing_fields: List[str]
    tips: List[str]


class ProfileUpdateRequest(BaseModel):
    # Core User fields
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None

    # Entrepreneur Profile fields
    stage: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[ExperienceItem]] = None
    education: Optional[List[EducationItem]] = None
    achievements: Optional[List[AchievementItem]] = None
    pitch_deck_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None

    # Sponsor Profile fields
    organization_name: Optional[str] = None
    logo_url: Optional[str] = None
    about: Optional[str] = None
    sponsor_type: Optional[str] = None
    focus_industries: Optional[List[str]] = None
    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    preferred_sponsorship_types: Optional[List[str]] = None
    sponsorship_interests: Optional[List[str]] = None
    areas_supported: Optional[List[str]] = None
    previous_collaborations: Optional[List[CollaborationItem]] = None


class ProjectSummary(BaseModel):
    id: int
    title: str
    slug: str
    tagline: str
    description: str
    category: str
    stage: str
    funding_goal: float
    current_funding: float
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicProfileRead(BaseModel):
    id: int
    username: Optional[str]
    full_name: str
    role: str
    is_verified: bool
    avatar_url: Optional[str]
    headline: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    created_at: datetime

    # Role details
    entrepreneur_profile: Optional[Dict[str, Any]] = None
    sponsor_profile: Optional[Dict[str, Any]] = None

    # Trust & Reputation
    trust_score: Optional[Dict[str, Any]] = None

    # Public Projects (if entrepreneur)
    projects: List[ProjectSummary] = []

    # Dynamic completion calculation
    completion: Optional[ProfileCompletionRead] = None
    is_own_profile: bool = False
