from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectRequirementBase(BaseModel):
    requirement_type: str  # capital, compute_credits, mentorship, hardware, cloud_resources, partnerships, other
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None


class ProjectRequirementCreate(ProjectRequirementBase):
    pass


class ProjectRequirementRead(ProjectRequirementBase):
    id: int
    project_id: int
    is_fulfilled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FounderInfoRead(BaseModel):
    id: int
    user_id: int
    full_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    trust_score: Optional[int] = 50
    is_verified: bool = False

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    tagline: str = Field(..., max_length=300)
    description: str
    category: str = "CleanTech"
    industry: Optional[str] = None
    stage: str = "idea"
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    target_market: Optional[str] = None
    value_proposition: Optional[str] = None
    current_progress: Optional[str] = None
    funding_goal: float = 0.0
    funding_received: float = 0.0
    currency: str = "INR"
    required_support: List[str] = Field(default_factory=list)
    required_resources: Optional[str] = None
    skills_needed: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    video_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    timeline: Optional[str] = None
    status: Optional[str] = None


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    tagline: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = "CleanTech"
    industry: Optional[str] = None
    stage: Optional[str] = "idea"
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    target_market: Optional[str] = None
    value_proposition: Optional[str] = None
    current_progress: Optional[str] = None
    funding_goal: float = 0.0
    funding_received: float = 0.0
    currency: Optional[str] = "INR"
    required_support: List[str] = Field(default_factory=list)
    required_resources: Optional[str] = None
    skills_needed: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    video_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    timeline: Optional[str] = None
    status: Optional[str] = None
    requirements: List[ProjectRequirementBase] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    problem_statement: Optional[str] = None
    proposed_solution: Optional[str] = None
    target_market: Optional[str] = None
    value_proposition: Optional[str] = None
    current_progress: Optional[str] = None
    funding_goal: Optional[float] = None
    funding_received: Optional[float] = None
    currency: Optional[str] = None
    required_support: Optional[List[str]] = None
    required_resources: Optional[str] = None
    skills_needed: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    website_url: Optional[str] = None
    demo_url: Optional[str] = None
    pitch_deck_url: Optional[str] = None
    video_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    timeline: Optional[str] = None
    status: Optional[str] = None
    requirements: Optional[List[ProjectRequirementBase]] = None


class ProjectRead(ProjectBase):
    id: int
    slug: str
    entrepreneur_id: int
    current_funding: float
    status: str
    created_at: datetime
    updated_at: datetime
    requirements: List[ProjectRequirementRead] = Field(default_factory=list)
    founder: Optional[FounderInfoRead] = None
    commitments_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDetailRead(ProjectRead):
    pass


class ProjectPaginationResponse(BaseModel):
    results: List[ProjectRead]
    total: int
    page: int
    limit: int
    total_pages: int
