from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy import select, func, update, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.communication import Conversation, Message
from app.models.user import User, SponsorProfile, EntrepreneurProfile
from app.models.project import Project
from app.models.sponsorship import (
    SponsorshipRequest,
    SponsorshipRequestStatus,
    SponsorshipCommitment,
    CommitmentStatus,
)
from app.models.ai_match import AIMatchExplanation
from app.schemas.communication import (
    ConversationCreate,
    ConversationRead,
    ConversationDetailRead,
    ParticipantSummary,
    MessageRead,
)
from app.services.notification_service import NotificationService


class MessagingService:
    @staticmethod
    async def check_relationship_authorization(
        db: AsyncSession, user_a_id: int, user_b_id: int
    ) -> bool:
        """
        Determines whether user_a and user_b are permitted to initiate a NEW conversation.
        Messaging authorization rules:
        1. PENDING Sponsorship Request -> Messaging allowed
        2. ACCEPTED Sponsorship Request -> Messaging allowed
        3. Active Sponsorship Commitment -> Messaging allowed (status != CANCELLED)
        4. Legitimate existing Vynk connection/match -> Messaging allowed according to match model
        5. REJECTED Sponsorship Request -> Do NOT allow creation of a NEW conversation solely because the rejected request exists
        6. CANCELLED Sponsorship Request -> Do NOT allow creation of a NEW conversation solely because the cancelled request exists
        7. Existing conversation created while the relationship was valid -> Handled in get_or_create_conversation / get_conversation_detail (preserved)
        """
        # 1 & 2. Check for PENDING or ACCEPTED SponsorshipRequest
        req_res = await db.execute(
            select(SponsorshipRequest).where(
                and_(
                    or_(
                        and_(SponsorshipRequest.sender_id == user_a_id, SponsorshipRequest.recipient_id == user_b_id),
                        and_(SponsorshipRequest.sender_id == user_b_id, SponsorshipRequest.recipient_id == user_a_id),
                    ),
                    SponsorshipRequest.status.in_([
                        SponsorshipRequestStatus.PENDING,
                        SponsorshipRequestStatus.ACCEPTED,
                    ]),
                )
            )
        )
        if req_res.scalars().first():
            return True

        # 3. Check for Active SponsorshipCommitment (joins sponsor & entrepreneur profiles to users; status != CANCELLED)
        comm_res = await db.execute(
            select(SponsorshipCommitment)
            .join(SponsorProfile, SponsorshipCommitment.sponsor_id == SponsorProfile.id)
            .join(EntrepreneurProfile, SponsorshipCommitment.entrepreneur_id == EntrepreneurProfile.id)
            .where(
                and_(
                    or_(
                        and_(SponsorProfile.user_id == user_a_id, EntrepreneurProfile.user_id == user_b_id),
                        and_(SponsorProfile.user_id == user_b_id, EntrepreneurProfile.user_id == user_a_id),
                    ),
                    SponsorshipCommitment.status != CommitmentStatus.CANCELLED,
                )
            )
        )
        if comm_res.scalars().first():
            return True

        # 4. Check for Legitimate connection / AI match record between participants
        match_res = await db.execute(
            select(AIMatchExplanation)
            .join(Project, AIMatchExplanation.project_id == Project.id)
            .join(EntrepreneurProfile, Project.entrepreneur_id == EntrepreneurProfile.id)
            .join(SponsorProfile, AIMatchExplanation.sponsor_id == SponsorProfile.id)
            .where(
                or_(
                    and_(EntrepreneurProfile.user_id == user_a_id, SponsorProfile.user_id == user_b_id),
                    and_(EntrepreneurProfile.user_id == user_b_id, SponsorProfile.user_id == user_a_id),
                )
            )
        )
        if match_res.scalars().first():
            return True

        # 5 & 6. REJECTED or CANCELLED requests alone DO NOT permit initiating a NEW conversation
        return False

    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession, current_user: User, data: ConversationCreate
    ) -> Conversation:
        if current_user.id == data.recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot start a conversation with yourself."
            )

        # Verify recipient exists
        recipient_res = await db.execute(select(User).where(User.id == data.recipient_id))
        recipient = recipient_res.scalar_one_or_none()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient user not found."
            )

        # Canonical ordering to enforce single thread per pair
        p1 = min(current_user.id, data.recipient_id)
        p2 = max(current_user.id, data.recipient_id)

        conv_res = await db.execute(
            select(Conversation).where(
                and_(Conversation.participant1_id == p1, Conversation.participant2_id == p2)
            )
        )
        conv = conv_res.scalar_one_or_none()

        if conv:
            # Existing conversation preserved (Correction Rule 7: preserve historical conversations)
            # Update context if provided and not yet set
            if data.project_id and not conv.project_id:
                conv.project_id = data.project_id
            if data.sponsorship_request_id and not conv.sponsorship_request_id:
                conv.sponsorship_request_id = data.sponsorship_request_id
            if data.commitment_id and not conv.commitment_id:
                conv.commitment_id = data.commitment_id

            if data.initial_message:
                await MessagingService.send_message(db, current_user, conv.id, data.initial_message)

            await db.commit()
            await db.refresh(conv)
            return conv

        # If NEW conversation, strictly enforce relationship authorization
        is_authorized = await MessagingService.check_relationship_authorization(
            db, current_user.id, data.recipient_id
        )
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Direct messaging requires an active platform relationship (pending/accepted sponsorship inquiry or active commitment)."
            )

        now = datetime.now(timezone.utc)
        new_conv = Conversation(
            participant1_id=p1,
            participant2_id=p2,
            project_id=data.project_id,
            sponsorship_request_id=data.sponsorship_request_id,
            commitment_id=data.commitment_id,
            last_message_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(new_conv)
        await db.commit()
        await db.refresh(new_conv)

        if data.initial_message:
            await MessagingService.send_message(db, current_user, new_conv.id, data.initial_message)
            await db.refresh(new_conv)

        return new_conv

    @staticmethod
    async def send_message(
        db: AsyncSession, current_user: User, conversation_id: int, content: str
    ) -> Message:
        clean_content = content.strip()
        if not clean_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content cannot be empty or whitespace only."
            )
        if len(clean_content) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content cannot exceed 5000 characters."
            )

        # Retrieve conversation
        conv_res = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )

        if current_user.id not in (conv.participant1_id, conv.participant2_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access unauthorized to this conversation."
            )

        recipient_id = conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id

        now = datetime.now(timezone.utc)
        msg = Message(
            conversation_id=conv.id,
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=clean_content,
            is_read=False,
            created_at=now,
        )
        db.add(msg)

        # Update conversation metadata
        conv.last_message_at = now
        conv.last_message_preview = clean_content[:100]
        conv.updated_at = now

        await db.commit()
        await db.refresh(msg)

        # Dispatch in-app notification to recipient
        preview_text = clean_content if len(clean_content) <= 80 else f"{clean_content[:77]}..."
        await NotificationService.create_notification(
            db=db,
            user_id=recipient_id,
            title=f"New Message from {current_user.full_name}",
            content=f'"{preview_text}"',
            type="new_message",
            entity_type="conversation",
            entity_id=conv.id,
            link=f"/messages?conversation_id={conv.id}",
        )

        return msg

    @staticmethod
    async def get_participant_summary(db: AsyncSession, user_id: int) -> ParticipantSummary:
        res = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.trust_score))
        )
        user = res.scalar_one_or_none()
        if not user:
            return ParticipantSummary(
                id=user_id,
                full_name="Vynk Member",
                role="member",
                trust_score=50,
                is_verified=False,
            )

        ts_score = 50
        if user.trust_score:
            ts_score = user.trust_score.score

        return ParticipantSummary(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            avatar_url=user.avatar_url,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            trust_score=ts_score,
            is_verified=bool(user.is_verified),
        )

    @staticmethod
    async def list_conversations(
        db: AsyncSession, current_user: User, limit: int = 50, offset: int = 0
    ) -> List[ConversationRead]:
        query = (
            select(Conversation)
            .where(
                or_(
                    Conversation.participant1_id == current_user.id,
                    Conversation.participant2_id == current_user.id,
                )
            )
            .order_by(Conversation.last_message_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await db.execute(query)
        conversations = list(res.scalars().all())

        results = []
        for conv in conversations:
            other_id = conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id
            other_summary = await MessagingService.get_participant_summary(db, other_id)

            # Calculate unread count for current_user
            unread_q = select(func.count(Message.id)).where(
                and_(
                    Message.conversation_id == conv.id,
                    Message.recipient_id == current_user.id,
                    Message.is_read == False,
                )
            )
            unread_count = (await db.execute(unread_q)).scalar() or 0

            # Project title context
            project_title = None
            if conv.project_id:
                p_res = await db.execute(select(Project.title).where(Project.id == conv.project_id))
                project_title = p_res.scalar_one_or_none()

            # Commitment status context
            comm_status = None
            if conv.commitment_id:
                c_res = await db.execute(
                    select(SponsorshipCommitment.status).where(SponsorshipCommitment.id == conv.commitment_id)
                )
                raw_status = c_res.scalar_one_or_none()
                comm_status = raw_status.value if hasattr(raw_status, "value") else str(raw_status) if raw_status else None

            # Compatibility score context if available
            compat_score = None
            if conv.project_id:
                # Find if an AI match explanation exists between this project and either participant
                match_q = (
                    select(AIMatchExplanation.compatibility_score)
                    .join(SponsorProfile, AIMatchExplanation.sponsor_id == SponsorProfile.id)
                    .where(
                        and_(
                            AIMatchExplanation.project_id == conv.project_id,
                            or_(
                                SponsorProfile.user_id == conv.participant1_id,
                                SponsorProfile.user_id == conv.participant2_id,
                            ),
                        )
                    )
                )
                compat_score = (await db.execute(match_q)).scalar_one_or_none()

            results.append(
                ConversationRead(
                    id=conv.id,
                    participant1_id=conv.participant1_id,
                    participant2_id=conv.participant2_id,
                    other_participant=other_summary,
                    project_id=conv.project_id,
                    project_title=project_title,
                    sponsorship_request_id=conv.sponsorship_request_id,
                    commitment_id=conv.commitment_id,
                    commitment_status=comm_status,
                    compatibility_score=compat_score,
                    last_message_at=conv.last_message_at,
                    last_message_preview=conv.last_message_preview,
                    unread_count=unread_count,
                    created_at=conv.created_at,
                )
            )

        return results

    @staticmethod
    async def get_conversation_detail(
        db: AsyncSession, current_user: User, conversation_id: int, limit: int = 100, offset: int = 0
    ) -> ConversationDetailRead:
        conv_res = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )

        if current_user.id not in (conv.participant1_id, conv.participant2_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access unauthorized to this conversation."
            )

        # Mark all incoming unread messages as read automatically
        now = datetime.now(timezone.utc)
        await db.execute(
            update(Message)
            .where(
                and_(
                    Message.conversation_id == conv.id,
                    Message.recipient_id == current_user.id,
                    Message.is_read == False,
                )
            )
            .values(is_read=True, read_at=now)
        )
        await db.commit()

        # Load messages
        msg_query = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        msg_res = await db.execute(msg_query)
        messages = list(msg_res.scalars().all())

        other_id = conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id
        other_summary = await MessagingService.get_participant_summary(db, other_id)

        project_title = None
        if conv.project_id:
            p_res = await db.execute(select(Project.title).where(Project.id == conv.project_id))
            project_title = p_res.scalar_one_or_none()

        comm_status = None
        if conv.commitment_id:
            c_res = await db.execute(
                select(SponsorshipCommitment.status).where(SponsorshipCommitment.id == conv.commitment_id)
            )
            raw_status = c_res.scalar_one_or_none()
            comm_status = raw_status.value if hasattr(raw_status, "value") else str(raw_status) if raw_status else None

        compat_score = None
        if conv.project_id:
            match_q = (
                select(AIMatchExplanation.compatibility_score)
                .join(SponsorProfile, AIMatchExplanation.sponsor_id == SponsorProfile.id)
                .where(
                    and_(
                        AIMatchExplanation.project_id == conv.project_id,
                        or_(
                            SponsorProfile.user_id == conv.participant1_id,
                            SponsorProfile.user_id == conv.participant2_id,
                        ),
                    )
                )
            )
            compat_score = (await db.execute(match_q)).scalar_one_or_none()

        return ConversationDetailRead(
            id=conv.id,
            participant1_id=conv.participant1_id,
            participant2_id=conv.participant2_id,
            other_participant=other_summary,
            project_id=conv.project_id,
            project_title=project_title,
            sponsorship_request_id=conv.sponsorship_request_id,
            commitment_id=conv.commitment_id,
            commitment_status=comm_status,
            compatibility_score=compat_score,
            last_message_at=conv.last_message_at,
            last_message_preview=conv.last_message_preview,
            unread_count=0,
            created_at=conv.created_at,
            messages=[MessageRead.model_validate(m) for m in messages],
        )

    @staticmethod
    async def mark_conversation_read(
        db: AsyncSession, current_user: User, conversation_id: int
    ) -> int:
        conv_res = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = conv_res.scalar_one_or_none()
        if not conv or current_user.id not in (conv.participant1_id, conv.participant2_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access unauthorized."
            )

        now = datetime.now(timezone.utc)
        result = await db.execute(
            update(Message)
            .where(
                and_(
                    Message.conversation_id == conv.id,
                    Message.recipient_id == current_user.id,
                    Message.is_read == False,
                )
            )
            .values(is_read=True, read_at=now)
        )
        await db.commit()
        return result.rowcount

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        query = select(func.count(Message.id)).where(
            and_(Message.recipient_id == user_id, Message.is_read == False)
        )
        count = (await db.execute(query)).scalar() or 0
        return count
