from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.communication import (
    ConversationCreate,
    ConversationRead,
    ConversationDetailRead,
    MessageCreate,
    MessageRead,
)
from app.services.messaging_service import MessagingService

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all active conversations for the authenticated user."""
    return await MessagingService.list_conversations(db, current_user, limit=limit, offset=offset)


@router.post("/conversations", response_model=ConversationDetailRead, status_code=status.HTTP_201_CREATED)
async def create_or_get_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a conversation or retrieve existing thread with authorization check."""
    conv = await MessagingService.get_or_create_conversation(db, current_user, data)
    return await MessagingService.get_conversation_detail(db, current_user, conv.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailRead)
async def get_conversation(
    conversation_id: int,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve message history for a specific conversation and mark incoming messages as read."""
    return await MessagingService.get_conversation_detail(
        db, current_user, conversation_id, limit=limit, offset=offset
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a new message within an existing authorized conversation."""
    return await MessagingService.send_message(
        db, current_user, conversation_id, data.content
    )


@router.patch("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Explicitly mark all incoming unread messages in a conversation as read."""
    count = await MessagingService.mark_conversation_read(db, current_user, conversation_id)
    return {"status": "success", "marked_read_count": count}


@router.get("/unread-count")
async def get_unread_message_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated user's total unread message count."""
    count = await MessagingService.get_unread_count(db, current_user.id)
    return {"unread_messages": count}
