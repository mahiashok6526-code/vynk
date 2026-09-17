from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TrustScoreFactor(BaseModel):
    name: str
    points: int
    max_points: int
    description: str


class TrustScoreEventRead(BaseModel):
    id: int
    event_type: str
    impact: int
    score_before: Optional[int] = None
    score_after: Optional[int] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrustScorePublicRead(BaseModel):
    id: int
    user_id: int
    score: int
    verification_points: int
    commitments_points: int
    responsiveness_points: int
    activity_points: int
    completed_commitments_count: int
    completed_milestones_count: int = 0
    avg_response_hours: int
    score_version: int = 1
    last_calculated_at: datetime
    factors: List[TrustScoreFactor] = []

    model_config = {"from_attributes": True}


class TrustScoreRead(TrustScorePublicRead):
    cancelled_commitments_count: int = 0
    events: List[TrustScoreEventRead] = []

    model_config = {"from_attributes": True}


class TrustScoreHistoryResponse(BaseModel):
    user_id: int
    current_score: int
    total_events: int
    events: List[TrustScoreEventRead]
