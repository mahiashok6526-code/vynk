from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.communication import (
    NotificationRead,
    NotificationListResponse,
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
    UnreadCountsResponse,
)
from app.services.notification_service import NotificationService
from app.services.messaging_service import MessagingService

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List authenticated user's notifications with optional filters."""
    items, total, unread = await NotificationService.list_notifications(
        db, current_user.id, limit=limit, offset=offset, unread_only=unread_only, type=type
    )
    return NotificationListResponse(
        items=[NotificationRead.model_validate(n) for n in items],
        total=total,
        unread_count=unread,
    )


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a specific notification as read."""
    notif = await NotificationService.mark_as_read(db, current_user.id, notification_id)
    return NotificationRead.model_validate(notif)


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread notifications for current user as read."""
    count = await NotificationService.mark_all_as_read(db, current_user.id)
    return {"status": "success", "marked_read_count": count}


@router.get("/unread-count")
async def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated user's total unread notification count."""
    count = await NotificationService.get_unread_count(db, current_user.id)
    return {"unread_notifications": count}


@router.get("/unread-summary", response_model=UnreadCountsResponse)
async def get_unread_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get authenticated user's unread counts for both messages and notifications."""
    notif_count = await NotificationService.get_unread_count(db, current_user.id)
    msg_count = await MessagingService.get_unread_count(db, current_user.id)
    return UnreadCountsResponse(
        unread_messages=msg_count,
        unread_notifications=notif_count,
    )


@router.get("/preferences", response_model=NotificationPreferenceRead)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve current user's in-app notification preferences."""
    pref = await NotificationService.get_or_create_preferences(db, current_user.id)
    return NotificationPreferenceRead.model_validate(pref)


@router.patch("/preferences", response_model=NotificationPreferenceRead)
async def update_notification_preferences(
    update_data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's in-app notification preferences."""
    pref = await NotificationService.update_preferences(db, current_user.id, update_data)
    return NotificationPreferenceRead.model_validate(pref)
