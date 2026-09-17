from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class TrustScore(Base, TimestampMixin):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    score = Column(Integer, default=50, nullable=False)  # Scaled 0 - 100

    # Supporting breakdown indicators
    verification_points = Column(Integer, default=0, nullable=False)   # e.g., max 25
    commitments_points = Column(Integer, default=20, nullable=False)   # e.g., max 35
    responsiveness_points = Column(Integer, default=15, nullable=False)# e.g., max 20
    activity_points = Column(Integer, default=15, nullable=False)      # e.g., max 20

    completed_commitments_count = Column(Integer, default=0, nullable=False)
    cancelled_commitments_count = Column(Integer, default=0, nullable=False)
    completed_milestones_count = Column(Integer, default=0, nullable=False)
    avg_response_hours = Column(Integer, default=24, nullable=False)
    score_version = Column(Integer, default=1, nullable=False)

    last_calculated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="trust_score")


class TrustScoreEvent(Base):
    __tablename__ = "trust_score_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # profile_verified, commitment_completed, milestone_completed, timely_response, etc.
    impact = Column(Integer, nullable=False)  # +5, -10, etc.
    score_before = Column(Integer, nullable=True)
    score_after = Column(Integer, nullable=True)
    reference_id = Column(Integer, nullable=True, index=True)
    reference_type = Column(String(50), nullable=True, index=True)  # commitment, milestone, sponsorship_request, profile
    reason = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="trust_events")
