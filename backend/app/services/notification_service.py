from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.communication import Notification, NotificationPreference
from app.schemas.communication import NotificationPreferenceUpdate


class NotificationService:
    @staticmethod
    async def get_or_create_preferences(db: AsyncSession, user_id: int) -> NotificationPreference:
        res = await db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        pref = res.scalar_one_or_none()
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                in_app_messages=True,
                in_app_sponsorship_requests=True,
                in_app_commitments=True,
                in_app_milestones=True,
                in_app_follow_ups=True,
                in_app_trust_score=True,
                email_notifications=False,
            )
            db.add(pref)
            await db.commit()
            await db.refresh(pref)
        return pref

    @staticmethod
    async def update_preferences(
        db: AsyncSession, user_id: int, update_data: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        pref = await NotificationService.get_or_create_preferences(db, user_id)
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(pref, field, value)
        pref.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(pref)
        return pref

    @staticmethod
    async def is_notification_enabled(db: AsyncSession, user_id: int, notif_type: str) -> bool:
        pref = await NotificationService.get_or_create_preferences(db, user_id)
        type_lower = (notif_type or "").lower()
        if "message" in type_lower:
            return pref.in_app_messages
        if "request" in type_lower or "sponsorship_request" in type_lower:
            return pref.in_app_sponsorship_requests
        if "milestone" in type_lower:
            return pref.in_app_milestones
        if "follow_up" in type_lower:
            return pref.in_app_follow_ups
        if "commitment" in type_lower:
            return pref.in_app_commitments
        if "trust" in type_lower:
            return pref.in_app_trust_score
        return True

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        link: Optional[str] = None,
    ) -> Optional[Notification]:
        # Check user preferences
        enabled = await NotificationService.is_notification_enabled(db, user_id, type)
        if not enabled:
            return None

        # Prevent duplicate notifications where the same backend event is retried
        if entity_type and entity_id:
            dup_filters = [
                Notification.user_id == user_id,
                Notification.type == type,
                Notification.entity_type == entity_type,
                Notification.entity_id == entity_id,
            ]
            if type == "follow_up":
                threshold = datetime.now(timezone.utc) - timedelta(hours=24)
            elif type in ("new_message", "message"):
                threshold = datetime.now(timezone.utc) - timedelta(seconds=30)
                dup_filters.append(Notification.content == content)
            else:
                threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
                dup_filters.append(Notification.title == title)

            dup_filters.append(Notification.created_at >= threshold)
            dup_res = await db.execute(select(Notification).where(and_(*dup_filters)))
            if dup_res.scalar_one_or_none():
                return None

        notif = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=type,
            link=link,
            entity_type=entity_type,
            entity_id=entity_id,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    @staticmethod
    async def list_notifications(
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
        type: Optional[str] = None,
    ) -> Tuple[List[Notification], int, int]:
        base_filter = [Notification.user_id == user_id]
        if unread_only:
            base_filter.append(Notification.is_read == False)
        if type:
            base_filter.append(Notification.type == type)

        # Count total matching
        count_query = select(func.count(Notification.id)).where(and_(*base_filter))
        total = (await db.execute(count_query)).scalar() or 0

        # Count total unread
        unread_query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        )
        unread_count = (await db.execute(unread_query)).scalar() or 0

        # Query items
        query = (
            select(Notification)
            .where(and_(*base_filter))
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await db.execute(query)
        items = list(res.scalars().all())

        return items, total, unread_count

    @staticmethod
    async def mark_as_read(db: AsyncSession, user_id: int, notification_id: int) -> Notification:
        res = await db.execute(
            select(Notification).where(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            )
        )
        notif = res.scalar_one_or_none()
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access unauthorized."
            )
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(notif)
        return notif

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
            .values(is_read=True, read_at=now)
        )
        await db.commit()
        return result.rowcount

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        query = select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id, Notification.is_read == False)
        )
        count = (await db.execute(query)).scalar() or 0
        return count
