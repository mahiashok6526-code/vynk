import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, Float, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ProjectStage(str, enum.Enum):
    IDEA = "idea"
    PROTOTYPE = "prototype"
    MVP = "mvp"
    LAUNCHED = "launched"
    SCALING = "scaling"


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SEEKING_SPONSORSHIP = "seeking_sponsorship"
    IN_DISCUSSION = "in_discussion"
    FUNDED = "funded"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ACTIVE = "active"  # backward compatibility with phase 1
    PAUSED = "paused"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    entrepreneur_id = Column(Integer, ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    tagline = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # AI, FinTech, CleanTech, EdTech, etc.
    industry = Column(String(100), nullable=True, index=True)
    stage = Column(SQLEnum(ProjectStage, name="project_stage_enum", native_enum=False), default=ProjectStage.IDEA, nullable=False)
    problem_statement = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    target_market = Column(Text, nullable=True)
    value_proposition = Column(Text, nullable=True)
    current_progress = Column(Text, nullable=True)
    funding_goal = Column(Float, default=0.0, nullable=False)
    funding_received = Column(Float, default=0.0, nullable=False)
    current_funding = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    required_support = Column(JSON, default=list, nullable=False)  # Capital, Compute Credits, Mentorship, Hardware, Cloud Resources, Partnerships, Other
    required_resources = Column(Text, nullable=True)
    skills_needed = Column(JSON, default=list, nullable=False)
    tech_stack = Column(JSON, default=list, nullable=False)
    demo_url = Column(String(512), nullable=True)
    website_url = Column(String(512), nullable=True)
    pitch_deck_url = Column(String(512), nullable=True)
    video_url = Column(String(512), nullable=True)
    cover_image_url = Column(String(512), nullable=True)
    logo_url = Column(String(512), nullable=True)
    location = Column(String(255), nullable=True)
    timeline = Column(String(255), nullable=True)
    status = Column(SQLEnum(ProjectStatus, name="project_status_enum", native_enum=False), default=ProjectStatus.SEEKING_SPONSORSHIP, nullable=False, index=True)
    moderation_status = Column(String(50), default="approved", nullable=False, index=True)
    moderation_reason = Column(Text, nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    moderated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    entrepreneur = relationship("EntrepreneurProfile", back_populates="projects")
    requirements = relationship("ProjectRequirement", back_populates="project", cascade="all, delete-orphan")
    sponsorship_requests = relationship("SponsorshipRequest", back_populates="project", cascade="all, delete-orphan")
    commitments = relationship("SponsorshipCommitment", back_populates="project", cascade="all, delete-orphan")


class ProjectRequirement(Base, TimestampMixin):
    __tablename__ = "project_requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_type = Column(String(50), nullable=False)  # capital, cloud_credits, mentorship, hardware, legal
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=True)  # optional monetary value
    is_fulfilled = Column(Boolean, default=False, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="requirements")
