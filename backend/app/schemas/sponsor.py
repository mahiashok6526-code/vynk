from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SponsorDiscoveryItem(BaseModel):
    id: int  # sponsor_profile id
    user_id: int
    full_name: str
    username: Optional[str] = None
    organization_name: Optional[str] = None
    logo_url: Optional[str] = None
    avatar_url: Optional[str] = None
    headline: Optional[str] = None
    about: Optional[str] = None
    industry: Optional[str] = None
    sponsor_type: str = "individual_angel"
    focus_industries: List[str] = Field(default_factory=list)
    min_budget: int = 1000
    max_budget: int = 50000
    currency: str = "INR"
    preferred_sponsorship_types: List[str] = Field(default_factory=list)
    sponsorship_interests: List[str] = Field(default_factory=list)
    areas_supported: List[str] = Field(default_factory=list)
    previous_collaborations: List[Dict[str, Any]] = Field(default_factory=list)
    location: Optional[str] = None
    is_verified: bool = False
    trust_score: int = 50
    created_at: datetime

    model_config = {"from_attributes": True}


class SponsorPaginationResponse(BaseModel):
    results: List[SponsorDiscoveryItem]
    total: int
    page: int
    limit: int
    total_pages: int
