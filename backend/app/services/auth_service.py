import re
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserRole, EntrepreneurProfile, SponsorProfile
from app.models.trust import TrustScore, TrustScoreEvent
from app.schemas.auth import RegisterRequest, LoginRequest, Token


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        query = (
            select(User)
            .where(User.email == email.lower())
            .options(
                selectinload(User.entrepreneur_profile),
                selectinload(User.sponsor_profile),
                selectinload(User.trust_score),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.entrepreneur_profile),
                selectinload(User.sponsor_profile),
                selectinload(User.trust_score),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def register(cls, db: AsyncSession, data: RegisterRequest) -> Token:
        # Check if email already registered
        existing = await cls.get_user_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        role = UserRole(data.role)
        hashed_password = get_password_hash(data.password)

        # Generate clean initial unique username
        base_username = re.sub(r'[^a-zA-Z0-9_]', '_', data.email.split('@')[0]).lower()
        if len(base_username) < 3:
            base_username = f"user_{base_username}"
        username_candidate = base_username[:25]

        # Ensure uniqueness
        existing_username = await db.execute(select(User).where(User.username == username_candidate))
        if existing_username.scalar_one_or_none():
            username_candidate = f"{username_candidate}_{uuid.uuid4().hex[:4]}"

        new_user = User(
            email=data.email.lower(),
            username=username_candidate,
            hashed_password=hashed_password,
            full_name=data.full_name,
            role=role,
            headline=data.headline,
            bio=data.bio,
            location=data.location,
            is_active=True,
            is_verified=False,
        )
        db.add(new_user)
        await db.flush()  # populate new_user.id

        # Create role-specific profile
        if role == UserRole.ENTREPRENEUR:
            profile = EntrepreneurProfile(
                user_id=new_user.id,
                stage=data.stage or "idea",
                industry=data.industry,
                skills=[],
            )
            db.add(profile)
        elif role == UserRole.SPONSOR:
            profile = SponsorProfile(
                user_id=new_user.id,
                organization_name=data.organization_name,
                sponsor_type=data.sponsor_type or "individual_angel",
                min_budget=data.min_budget or 1000,
                max_budget=data.max_budget or 50000,
                focus_industries=[],
                preferred_sponsorship_types=["grant", "mentorship"],
            )
            db.add(profile)

        # Initialize base Trust Score (50/100 default starter score)
        initial_trust = TrustScore(
            user_id=new_user.id,
            score=50,
            verification_points=0,
            commitments_points=20,
            responsiveness_points=15,
            activity_points=15,
            completed_commitments_count=0,
            cancelled_commitments_count=0,
            avg_response_hours=24,
        )
        db.add(initial_trust)

        # Log initial registration trust score event
        init_event = TrustScoreEvent(
            user_id=new_user.id,
            event_type="account_created",
            impact=50,
            reason="Initial baseline trust score established upon verified registration.",
        )
        db.add(init_event)

        await db.commit()
        await db.refresh(new_user)

        # Generate JWT
        token_str = create_access_token(
            subject=new_user.id,
            role=new_user.role.value
        )

        return Token(
            access_token=token_str,
            token_type="bearer",
            role=new_user.role.value,
            user_id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
        )

    @classmethod
    async def login(cls, db: AsyncSession, data: LoginRequest) -> Token:
        user = await cls.get_user_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact support.",
            )

        token_str = create_access_token(
            subject=user.id,
            role=user.role.value
        )

        return Token(
            access_token=token_str,
            token_type="bearer",
            role=user.role.value,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )
