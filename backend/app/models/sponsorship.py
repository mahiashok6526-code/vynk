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
    sponsorship_type = Column(String(100), default="financial", nullable=False)
    status = Column(
        SQLEnum(SponsorshipRequestStatus, name="sponsorship_request_status_enum", native_enum=False),
        default=SponsorshipRequestStatus.PENDING,
        nullable=False,
        index=True
    )

    # Relationships
    project = relationship("Project", back_populates="sponsorship_requests")
    commitment = relationship("SponsorshipCommitment", back_populates="request", uselist=False)


class SponsorshipCommitment(Base, TimestampMixin):
    __tablename__ = "sponsorship_commitments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    entrepreneur_id = Column(Integer, ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    request_id = Column(Integer, ForeignKey("sponsorship_requests.id", ondelete="SET NULL"), nullable=True)

    amount = Column(Float, nullable=False)
    sponsorship_type = Column(String(100), nullable=False)  # grant, equity, convertible_note, credits, equipment
    status = Column(
        SQLEnum(CommitmentStatus, name="commitment_status_enum", native_enum=False),
        default=CommitmentStatus.INTERESTED,
        nullable=False,
        index=True
    )
    expected_date = Column(DateTime(timezone=True), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True, index=True)
    agreement_reference = Column(String(255), nullable=True)
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
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    commitment = relationship("SponsorshipCommitment", back_populates="updates")
