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
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrustScoreRead(BaseModel):
    id: int
    user_id: int
    score: int
    verification_points: int
    commitments_points: int
    responsiveness_points: int
    activity_points: int
    completed_commitments_count: int
    cancelled_commitments_count: int
    avg_response_hours: int
    last_calculated_at: datetime
    factors: List[TrustScoreFactor] = []
    events: List[TrustScoreEventRead] = []

    model_config = {"from_attributes": True}
