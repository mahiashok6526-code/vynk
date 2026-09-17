import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, DateTime, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    INVESTIGATING = "investigating"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportCategory(str, enum.Enum):
    SPAM = "spam"
    FRAUD = "fraud"
    ABUSE = "abuse"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    MISREPRESENTATION = "misrepresentation"
    OTHER = "other"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class DisputeReason(str, enum.Enum):
    COMMITMENT_DISAGREEMENT = "commitment_disagreement"
    DELIVERY_ISSUE = "delivery_issue"
    MISREPRESENTATION = "misrepresentation"
    CANCELLATION_DISPUTE = "cancellation_dispute"
    OTHER = "other"


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_type = Column(String(100), nullable=False)  # identity, business_registration, accredited_investor, domain
    status = Column(
        SQLEnum(VerificationStatus, name="verification_status_enum", native_enum=False),
        default=VerificationStatus.PENDING,
        nullable=False,
        index=True
    )
    document_url = Column(String(512), nullable=True)
    notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="verification_records")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_sponsorship_request_id = Column(Integer, ForeignKey("sponsorship_requests.id", ondelete="SET NULL"), nullable=True, index=True)
    reported_commitment_id = Column(Integer, ForeignKey("sponsorship_commitments.id", ondelete="SET NULL"), nullable=True, index=True)
    
    category = Column(String(50), default="other", nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ReportStatus, name="report_status_enum", native_enum=False),
        default=ReportStatus.PENDING,
        nullable=False,
        index=True
    )
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    reported_user = relationship("User", foreign_keys=[reported_user_id])
    reported_project = relationship("Project", foreign_keys=[reported_project_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("sponsorship_commitments.id", ondelete="SET NULL"), nullable=True, index=True)
    request_id = Column(Integer, ForeignKey("sponsorship_requests.id", ondelete="SET NULL"), nullable=True, index=True)
    initiator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        SQLEnum(DisputeStatus, name="dispute_status_enum", native_enum=False),
        default=DisputeStatus.OPEN,
        nullable=False,
        index=True
    )
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id])
    respondent = relationship("User", foreign_keys=[respondent_id])
    commitment = relationship("SponsorshipCommitment", foreign_keys=[commitment_id])
    request = relationship("SponsorshipRequest", foreign_keys=[request_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])

    @property
    def details(self):
        return self.metadata_json or {}
