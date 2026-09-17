import re
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserRole, EntrepreneurProfile, SponsorProfile
from app.models.project import Project, ProjectStatus
from app.schemas.profile import ProfileCompletionRead, ProfileUpdateRequest


class ProfileService:
    USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

    @classmethod
    def calculate_completion(cls, user: User) -> ProfileCompletionRead:
        """Dynamically computes the profile completion percentage, completed fields, and tips."""
        completed_fields = []
        missing_fields = []
        tips = []
        total_percentage = 0

        if user.role == UserRole.ENTREPRENEUR:
            ep = user.entrepreneur_profile

            # 1. Avatar (10%)
            if user.avatar_url and user.avatar_url.strip():
                completed_fields.append("Profile Photo")
                total_percentage += 10
            else:
                missing_fields.append("Profile Photo")
                tips.append("Add a profile photo to build initial trust with sponsors (+10%)")

            # 2. Username & Full Name (10%)
            if user.username and user.full_name:
                completed_fields.append("Full Name & Username")
                total_percentage += 10
            else:
                missing_fields.append("Full Name & Username")
                tips.append("Set your custom @username and full name (+10%)")

            # 3. Bio / Headline (10%)
            if (user.headline and user.headline.strip()) or (user.bio and user.bio.strip()):
                completed_fields.append("Short Bio & Headline")
                total_percentage += 10
            else:
                missing_fields.append("Short Bio & Headline")
                tips.append("Write a compelling short bio and headline summarizing your vision (+10%)")

            # 4. Location (10%)
            if user.location and user.location.strip():
                completed_fields.append("Location")
                total_percentage += 10
            else:
                missing_fields.append("Location")
                tips.append("Add your location so local sponsors can discover you (+10%)")

            # 5. Industry & Stage (10%)
            if ep and ep.industry and ep.industry.strip():
                completed_fields.append("Industry & Stage")
                total_percentage += 10
            else:
                missing_fields.append("Industry & Stage")
                tips.append("Specify your primary industry and startup stage (+10%)")

            # 6. Skills (15%)
            if ep and ep.skills and len(ep.skills) > 0:
                completed_fields.append("Key Skills")
                total_percentage += 15
            else:
                missing_fields.append("Key Skills")
                tips.append("Add your core skills (e.g. AI/ML, Full-Stack, Hardware) (+15%)")

            # 7. Experience (15%)
            if ep and ep.experience and len(ep.experience) > 0:
                completed_fields.append("Professional Experience")
                total_percentage += 15
            else:
                missing_fields.append("Professional Experience")
                tips.append("Add your background and prior roles (+15%)")

            # 8. Education (10%)
            if ep and ep.education and len(ep.education) > 0:
                completed_fields.append("Education")
                total_percentage += 10
            else:
                missing_fields.append("Education")
                tips.append("List your educational background or degrees (+10%)")

            # 9. Achievements (10%)
            if ep and ep.achievements and len(ep.achievements) > 0:
                completed_fields.append("Achievements & Awards")
                total_percentage += 10
            else:
                missing_fields.append("Achievements & Awards")
                tips.append("Highlight your hackathon wins, grants, patents, or awards (+10%)")

        elif user.role == UserRole.SPONSOR:
            sp = user.sponsor_profile

            # 1. Organization Logo / Avatar (10%)
            if (sp and sp.logo_url and sp.logo_url.strip()) or (user.avatar_url and user.avatar_url.strip()):
                completed_fields.append("Organization Logo")
                total_percentage += 10
            else:
                missing_fields.append("Organization Logo")
                tips.append("Upload your fund or organization brand logo (+10%)")

            # 2. Organization Name (15%)
            if sp and sp.organization_name and sp.organization_name.strip():
                completed_fields.append("Organization Name")
                total_percentage += 15
            else:
                missing_fields.append("Organization Name")
                tips.append("Set your company or fund organization name (+15%)")

            # 3. About & Overview (15%)
            if (sp and sp.about and sp.about.strip()) or (user.bio and user.bio.strip()):
                completed_fields.append("About Organization")
                total_percentage += 15
            else:
                missing_fields.append("About Organization")
                tips.append("Provide an overview of your organization and investment philosophy (+15%)")

            # 4. Location (10%)
            if user.location and user.location.strip():
                completed_fields.append("Location / HQ")
                total_percentage += 10
            else:
                missing_fields.append("Location / HQ")
                tips.append("Add your headquarters or operating location (+10%)")

            # 5. Industry Focus (10%)
            if (sp and sp.industry and sp.industry.strip()) or (sp and sp.focus_industries and len(sp.focus_industries) > 0):
                completed_fields.append("Industry Focus")
                total_percentage += 10
            else:
                missing_fields.append("Industry Focus")
                tips.append("Define your primary focus industries (+10%)")

            # 6. Sponsorship Interests (15%)
            if sp and sp.sponsorship_interests and len(sp.sponsorship_interests) > 0:
                completed_fields.append("Sponsorship Interests")
                total_percentage += 15
            else:
                missing_fields.append("Sponsorship Interests")
                tips.append("List startup stages and categories you are interested in backing (+15%)")

            # 7. Areas Supported (15%)
            if sp and sp.areas_supported and len(sp.areas_supported) > 0:
                completed_fields.append("Areas Supported")
                total_percentage += 15
            else:
                missing_fields.append("Areas Supported")
                tips.append("Specify support types provided (Capital, Mentorship, Credits, Labs) (+15%)")

            # 8. Previous Collaborations (10%)
            if sp and sp.previous_collaborations and len(sp.previous_collaborations) > 0:
                completed_fields.append("Previous Collaborations")
                total_percentage += 10
            else:
                missing_fields.append("Previous Collaborations")
                tips.append("Highlight past projects or portfolio startups you supported (+10%)")

        else:
            # Admin or other role default
            total_percentage = 100
            completed_fields.append("System Administrator Profile")

        # Clamp between 0 and 100
        total_percentage = max(0, min(100, total_percentage))

        return ProfileCompletionRead(
            percentage=total_percentage,
            completed_fields=completed_fields,
            missing_fields=missing_fields,
            tips=tips[:3],  # return top 3 actionable tips
        )

    @classmethod
    async def get_user_by_identifier(cls, db: AsyncSession, identifier: str) -> Optional[User]:
        """Look up user by either numeric id or username."""
        query = (
            select(User)
            .options(
                selectinload(User.entrepreneur_profile).selectinload(EntrepreneurProfile.projects),
                selectinload(User.sponsor_profile),
                selectinload(User.trust_score),
            )
        )

        if identifier.isdigit():
            user_id = int(identifier)
            result = await db.execute(query.where(or_(User.id == user_id, User.username == identifier)))
        else:
            result = await db.execute(query.where(User.username == identifier.lower()))

        return result.scalar_one_or_none()

    @classmethod
    async def update_profile(cls, db: AsyncSession, user: User, update_data: ProfileUpdateRequest) -> User:
        """Validates and updates profile information for the authenticated user."""
        # 1. Username validation & uniqueness check
        if update_data.username is not None:
            new_username = update_data.username.strip().lower()
            if not cls.USERNAME_REGEX.match(new_username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username must be 3-30 characters and contain only letters, numbers, and underscores.",
                )

            # Check if username taken by another user
            existing = await db.execute(
                select(User).where(User.username == new_username, User.id != user.id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The username '{new_username}' is already taken. Please choose another.",
                )
            user.username = new_username

        # 2. Update core user fields
        if update_data.full_name is not None:
            user.full_name = update_data.full_name.strip()
        if update_data.headline is not None:
            user.headline = update_data.headline.strip() if update_data.headline else None
        if update_data.bio is not None:
            user.bio = update_data.bio.strip() if update_data.bio else None
        if update_data.location is not None:
            user.location = update_data.location.strip() if update_data.location else None
        if update_data.avatar_url is not None:
            user.avatar_url = update_data.avatar_url.strip() if update_data.avatar_url else None

        # 3. Update role-specific profile fields
        if user.role == UserRole.ENTREPRENEUR and user.entrepreneur_profile:
            ep = user.entrepreneur_profile
            if update_data.stage is not None:
                ep.stage = update_data.stage
            if update_data.industry is not None:
                ep.industry = update_data.industry
            if update_data.skills is not None:
                ep.skills = [s.strip() for s in update_data.skills if s.strip()]
            if update_data.experience is not None:
                ep.experience = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in update_data.experience
                ]
            if update_data.education is not None:
                ep.education = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in update_data.education
                ]
            if update_data.achievements is not None:
                ep.achievements = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in update_data.achievements
                ]
            if update_data.pitch_deck_url is not None:
                ep.pitch_deck_url = update_data.pitch_deck_url
            if update_data.linkedin_url is not None:
                ep.linkedin_url = update_data.linkedin_url
            if update_data.github_url is not None:
                ep.github_url = update_data.github_url
            if update_data.website_url is not None:
                ep.website_url = update_data.website_url

        elif user.role == UserRole.SPONSOR and user.sponsor_profile:
            sp = user.sponsor_profile
            if update_data.organization_name is not None:
                sp.organization_name = update_data.organization_name.strip()
            if update_data.logo_url is not None:
                sp.logo_url = update_data.logo_url.strip() if update_data.logo_url else None
            if update_data.about is not None:
                sp.about = update_data.about.strip() if update_data.about else None
            if update_data.industry is not None:
                sp.industry = update_data.industry
            if update_data.sponsor_type is not None:
                sp.sponsor_type = update_data.sponsor_type
            if update_data.focus_industries is not None:
                sp.focus_industries = [fi.strip() for fi in update_data.focus_industries if fi.strip()]
            if update_data.min_budget is not None:
                sp.min_budget = update_data.min_budget
            if update_data.max_budget is not None:
                sp.max_budget = update_data.max_budget
            if update_data.preferred_sponsorship_types is not None:
                sp.preferred_sponsorship_types = update_data.preferred_sponsorship_types
            if update_data.sponsorship_interests is not None:
                sp.sponsorship_interests = [si.strip() for si in update_data.sponsorship_interests if si.strip()]
            if update_data.areas_supported is not None:
                sp.areas_supported = [area.strip() for area in update_data.areas_supported if area.strip()]
            if update_data.previous_collaborations is not None:
                sp.previous_collaborations = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in update_data.previous_collaborations
                ]

        await db.commit()
        await db.refresh(user)
        return user
