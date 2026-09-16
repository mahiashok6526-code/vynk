from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectRequirementBase(BaseModel):
    requirement_type: str  # capital, credits, mentorship, hardware, legal
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None


class ProjectRequirementRead(ProjectRequirementBase):
    id: int
    project_id: int
    is_fulfilled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    tagline: str = Field(..., max_length=300)
    description: str
    category: str
    stage: str = "idea"
    funding_goal: float = 0.0
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    requirements: List[ProjectRequirementBase] = []


class ProjectRead(ProjectBase):
    id: int
    slug: str
    entrepreneur_id: int
    current_funding: float
    status: str
    created_at: datetime
    updated_at: datetime
    requirements: List[ProjectRequirementRead] = []

    model_config = {"from_attributes": True}
