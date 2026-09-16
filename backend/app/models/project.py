import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, Float, Boolean, JSON
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
    ACTIVE = "active"
    FUNDED = "funded"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    entrepreneur_id = Column(Integer, ForeignKey("entrepreneur_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    tagline = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # AI, FinTech, CleanTech, EdTech, etc.
    stage = Column(SQLEnum(ProjectStage, name="project_stage_enum", native_enum=False), default=ProjectStage.IDEA, nullable=False)
    funding_goal = Column(Float, default=0.0, nullable=False)
    current_funding = Column(Float, default=0.0, nullable=False)
    demo_url = Column(String(512), nullable=True)
    pitch_deck_url = Column(String(512), nullable=True)
    status = Column(SQLEnum(ProjectStatus, name="project_status_enum", native_enum=False), default=ProjectStatus.ACTIVE, nullable=False, index=True)

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
