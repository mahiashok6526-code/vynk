import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, Float, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SponsorshipRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class CommitmentStatus(str, enum.Enum):
    INTERESTED = "interested"
    DISCUSSION = "discussion"
    PROMISED = "promised"
    CONFIRMED = "confirmed"
    AGREEMENT = "agreement"
    FUNDED = "funded"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SponsorshipRequest(Base, TimestampMixin):
    __tablename__ = "sponsorship_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    requested_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="INR", nullable=False)
    sponsorship_type = Column(String(100), default="financial", nullable=False)
    requested_resources = Column(Text, nullable=True)
    response_note = Column(Text, nullable=True)
    status = Column(
        SQLEnum(SponsorshipRequestStatus, name="sponsorship_request_status_enum", native_enum=False),
        default=SponsorshipRequestStatus.PENDING,
        nullable=False,
        index=True
    )

    # Relationships
    project = relationship("Project", back_populates="sponsorship_requests")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    commitment = relationship("SponsorshipCommitment", back_populates="request", uselist=False)


class SponsorshipCommitment(Base, TimestampMixin):
    __tablename__ = "sponsorship_commitments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    entrepreneur_id = Column(Integer, ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    request_id = Column(Integer, ForeignKey("sponsorship_requests.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Float, default=0.0, nullable=True)
    currency = Column(String(10), default="INR", nullable=False)
    sponsorship_type = Column(String(100), nullable=False)  # Financial Funding, Hardware, Software / Cloud Credits, Mentorship, etc.
    status = Column(
        SQLEnum(CommitmentStatus, name="commitment_status_enum", native_enum=False),
        default=CommitmentStatus.INTERESTED,
        nullable=False,
        index=True
    )
    expected_date = Column(DateTime(timezone=True), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True, index=True)
    follow_up_reason = Column(String(255), nullable=True)
    agreement_reference = Column(String(255), nullable=True)
    cancellation_type = Column(String(50), nullable=True)  # mutual, unilateral
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="commitments")
    sponsor = relationship("SponsorProfile", back_populates="commitments")
    entrepreneur = relationship("EntrepreneurProfile", back_populates="commitments")
    request = relationship("SponsorshipRequest", back_populates="commitment")
    updates = relationship("CommitmentUpdate", back_populates="commitment", cascade="all, delete-orphan", order_by="CommitmentUpdate.created_at.desc()")


class CommitmentUpdate(Base):
    __tablename__ = "commitment_updates"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("sponsorship_commitments.id", ondelete="CASCADE"), nullable=False, index=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    update_type = Column(String(50), default="status_change", nullable=False)  # status_change, milestone, fund_transfer, resource_delivered, note
    title = Column(String(255), nullable=True)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    cancellation_type = Column(String(50), nullable=True)  # mutual, unilateral
    note = Column(Text, nullable=False)
    evidence_reference = Column(String(512), nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    commitment = relationship("SponsorshipCommitment", back_populates="updates")
    updater = relationship("User", foreign_keys=[updated_by])

