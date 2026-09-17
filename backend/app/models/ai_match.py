from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class AIMatchExplanation(Base, TimestampMixin):
    """Stores computed AI/deterministic match explanations and factor breakdowns.

    Caches explanations to prevent redundant LLM invocations and provides
    auditable historical records of compatibility scoring.
    """
    __tablename__ = "ai_match_explanations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    compatibility_score = Column(Integer, nullable=False)
    factors = Column(JSON, nullable=False, default=dict)
    reasons = Column(JSON, nullable=False, default=list)
    mismatches = Column(JSON, nullable=False, default=list)
    explanation = Column(Text, nullable=False)

    ai_generated = Column(Boolean, default=False, nullable=False)
    provider = Column(String(50), default="deterministic", nullable=False)
    model = Column(String(100), default="compatibility_v1", nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "sponsor_id", name="uq_project_sponsor_match"),
    )
