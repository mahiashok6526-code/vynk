from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class FactorScoreDetail(BaseModel):
    name: str
    score: int
    max_score: int
    percentage: int
    detail: str


class ProjectMatchItem(BaseModel):
    project_id: int
    title: str
    tagline: str
    category: str
    industry: Optional[str] = None
    stage: str
    funding_goal: float
    current_funding: float = 0.0
    currency: str = "INR"
    required_support: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    logo_url: Optional[str] = None
    founder_name: str
    founder_username: Optional[str] = None
    trust_score: int = 50
    is_verified: bool = False
    compatibility_score: int
    factors: Dict[str, FactorScoreDetail]
    reasons: List[str] = Field(default_factory=list)
    mismatches: List[str] = Field(default_factory=list)
    summary: str


class SponsorMatchItem(BaseModel):
    sponsor_id: int
    user_id: int
    full_name: str
    username: Optional[str] = None
    organization_name: Optional[str] = None
    sponsor_type: str = "angel"
    logo_url: Optional[str] = None
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    focus_industries: List[str] = Field(default_factory=list)
    preferred_sponsorship_types: List[str] = Field(default_factory=list)
    areas_supported: List[str] = Field(default_factory=list)
    min_budget: int = 1000
    max_budget: int = 100000
    currency: str = "INR"
    location: Optional[str] = None
    trust_score: int = 50
    is_verified: bool = False
    compatibility_score: int
    factors: Dict[str, FactorScoreDetail]
    reasons: List[str] = Field(default_factory=list)
    mismatches: List[str] = Field(default_factory=list)
    summary: str


class MatchExplanationResponse(BaseModel):
    project_id: int
    sponsor_id: int
    project_title: str
    sponsor_name: str
    compatibility_score: int
    trust_score: int
    factors: Dict[str, FactorScoreDetail]
    reasons: List[str] = Field(default_factory=list)
    mismatches: List[str] = Field(default_factory=list)
    explanation: str
    ai_generated: bool
    provider: str
    model: str
    generated_at: datetime
