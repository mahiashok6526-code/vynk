import enum
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    ENTREPRENEUR = "entrepreneur"
    SPONSOR = "sponsor"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, name="user_role_enum", native_enum=False), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(512), nullable=True)
    headline = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)

    # Relationships
    entrepreneur_profile = relationship("EntrepreneurProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sponsor_profile = relationship("SponsorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trust_score = relationship("TrustScore", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trust_events = relationship("TrustScoreEvent", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    verification_records = relationship("VerificationRecord", foreign_keys="VerificationRecord.user_id", back_populates="user", cascade="all, delete-orphan")


class EntrepreneurProfile(Base, TimestampMixin):
    __tablename__ = "entrepreneur_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    stage = Column(String(50), default="idea", nullable=False)  # idea, prototype, mvp, scaling
    industry = Column(String(100), nullable=True, index=True)  # AI/DeepTech, FinTech, HealthTech, etc.
    skills = Column(JSON, default=list, nullable=False)  # List of strings
    pitch_deck_url = Column(String(512), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    website_url = Column(String(512), nullable=True)

    # Relationships
    user = relationship("User", back_populates="entrepreneur_profile")
    projects = relationship("Project", back_populates="entrepreneur", cascade="all, delete-orphan")
    commitments = relationship("SponsorshipCommitment", back_populates="entrepreneur")


class SponsorProfile(Base, TimestampMixin):
    __tablename__ = "sponsor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    organization_name = Column(String(255), nullable=True)
    sponsor_type = Column(String(100), default="individual_angel", nullable=False)  # angel, corporate, fund, grant
    focus_industries = Column(JSON, default=list, nullable=False)  # list of target industries
    min_budget = Column(Integer, default=1000, nullable=False)
    max_budget = Column(Integer, default=50000, nullable=False)
    preferred_sponsorship_types = Column(JSON, default=list, nullable=False)  # grant, equity, credits, mentorship

    # Relationships
    user = relationship("User", back_populates="sponsor_profile")
    commitments = relationship("SponsorshipCommitment", back_populates="sponsor")
