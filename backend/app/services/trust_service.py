from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.trust import TrustScore, TrustScoreEvent
from app.models.user import User
from app.models.sponsorship import SponsorshipCommitment, CommitmentStatus
from app.schemas.trust import (
    TrustScoreRead,
    TrustScorePublicRead,
    TrustScoreFactor,
    TrustScoreEventRead,
    TrustScoreHistoryResponse,
)


class TrustService:
    @staticmethod
    async def get_or_create_trust_score(db: AsyncSession, user_id: int) -> TrustScore:
        query = select(TrustScore).where(TrustScore.user_id == user_id)
        result = await db.execute(query)
        ts = result.scalar_one_or_none()

        if not ts:
            ts = TrustScore(
                user_id=user_id,
                score=50,
                score_version=1,
                verification_points=0,
                commitments_points=20,
                responsiveness_points=15,
                activity_points=15,
                completed_commitments_count=0,
                cancelled_commitments_count=0,
                completed_milestones_count=0,
                avg_response_hours=24,
            )
            db.add(ts)
            await db.commit()
            await db.refresh(ts)
        return ts

    @classmethod
    async def recalculate_trust_score(cls, db: AsyncSession, user_id: int) -> TrustScore:
        """Single Source of Truth deterministic Trust Score calculator.
        
        Evaluates verifiable platform signals and idempotent events:
        1. Verification (0-25): Platform identity verification (+15) + profile completion (+10).
        2. Commitments (0-35): Base 20 + fulfilled commitments (+5 each) - unilateral cancellations (-10 each).
        3. Milestones (0-20): Base 15 + validated milestones (+2 each, max 2 per commitment).
        4. Activity & Responsiveness (0-20): Base 15 + timely responses (+2 each) + project updates (+2 each).
        
        Total clamped to [0, 100].
        """
        ts = await cls.get_or_create_trust_score(db, user_id)

        # 1. Verification pillar (Max 25)
        u_query = select(User).where(User.id == user_id).options(
            selectinload(User.entrepreneur_profile),
            selectinload(User.sponsor_profile),
        )
        u_res = await db.execute(u_query)
        user = u_res.scalar_one_or_none()

        v_points = 0
        if user and user.is_verified:
            v_points += 15
        
        # Check profile completion if available
        completion = 0
        if user:
            from app.services.profile_service import ProfileService
            comp_res = ProfileService.calculate_completion(user)
            completion = comp_res.percentage
        if completion >= 100:
            v_points += 10
        elif completion >= 80:
            v_points += 5
        v_points = min(25, max(0, v_points))

        # Fetch all recorded events for this user to aggregate factual outcomes
        events_q = select(TrustScoreEvent).where(TrustScoreEvent.user_id == user_id)
        events_res = await db.execute(events_q)
        all_events = events_res.scalars().all()

        # 2. Commitment pillar (Base 20, Range 0 - 35)
        completed_count = 0
        unilateral_cancel_count = 0
        seen_commitments = set()

        for ev in all_events:
            if ev.event_type == "commitment_completed":
                cid = ev.reference_id or ev.id
                if cid not in seen_commitments:
                    seen_commitments.add(cid)
                    completed_count += 1
            elif ev.event_type == "commitment_cancelled_unilateral":
                unilateral_cancel_count += 1

        c_points = min(35, max(0, 20 + (completed_count * 5) - (unilateral_cancel_count * 10)))

        # 3. Milestone reliability pillar (Base 15, Range 0 - 20)
        # Anti-gaming: Max 2 rewarded milestones per commitment
        milestones_per_commitment = {}
        total_valid_milestones = 0
        for ev in all_events:
            if ev.event_type == "milestone_completed":
                comm_key = ev.reference_type if (ev.reference_type and "commitment_milestone_" in ev.reference_type) else str(ev.reference_id or 0)
                count = milestones_per_commitment.get(comm_key, 0)
                if count < 2:
                    milestones_per_commitment[comm_key] = count + 1
                    total_valid_milestones += 1

        m_points = min(20, max(0, 15 + (total_valid_milestones * 2)))

        # 4. Responsiveness & Platform Activity (Base 15, Range 0 - 20)
        timely_responses = sum(1 for ev in all_events if ev.event_type == "timely_response")
        project_updates = sum(1 for ev in all_events if ev.event_type == "project_update")
        r_points = min(20, max(0, 15 + (timely_responses * 2) + (project_updates * 2)))

        # Final aggregate score
        total_score = min(100, max(0, v_points + c_points + m_points + r_points))

        ts.verification_points = v_points
        ts.commitments_points = c_points
        ts.responsiveness_points = m_points  # Milestone reliability dimension
        ts.activity_points = r_points        # Communication & activity dimension
        ts.completed_commitments_count = completed_count
        ts.cancelled_commitments_count = unilateral_cancel_count
        ts.completed_milestones_count = total_valid_milestones
        ts.score = total_score
        ts.last_calculated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(ts)
        return ts

    @classmethod
    async def record_event(
        cls,
        db: AsyncSession,
        user_id: int,
        event_type: str,
        impact: int,
        reason: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
    ) -> Tuple[TrustScore, bool]:
        """Records an auditable trust event idempotently and deterministically updates score.
        
        Returns (trust_score, is_new_event).
        """
        ts = await cls.get_or_create_trust_score(db, user_id)

        # Idempotency check: prevent duplicate reward for the same reference
        if reference_type and reference_id is not None:
            existing_q = select(TrustScoreEvent).where(
                and_(
                    TrustScoreEvent.user_id == user_id,
                    TrustScoreEvent.event_type == event_type,
                    TrustScoreEvent.reference_type == reference_type,
                    TrustScoreEvent.reference_id == reference_id,
                )
            )
            existing_res = await db.execute(existing_q)
            if existing_res.scalar_one_or_none():
                # Already processed this exact event
                return ts, False

        score_before = ts.score

        # Persist event
        event = TrustScoreEvent(
            user_id=user_id,
            event_type=event_type,
            impact=impact,
            score_before=score_before,
            score_after=score_before,  # Updated after recalculation
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
        )
        db.add(event)
        await db.flush()

        # Recalculate deterministically to ensure incremental == recalculated
        updated_ts = await cls.recalculate_trust_score(db, user_id)

        # Update event snapshot
        event.score_after = updated_ts.score
        await db.commit()
        await db.refresh(updated_ts)

        if updated_ts.score != score_before:
            try:
                from app.services.notification_service import NotificationService
                delta = updated_ts.score - score_before
                sign = f"+{delta}" if delta > 0 else f"{delta}"
                await NotificationService.create_notification(
                    db,
                    user_id=user_id,
                    title="Trust Score Updated",
                    content=f"Your Trust Score changed by {sign} to {updated_ts.score} ({reason}).",
                    type="trust_score_updated",
                    entity_type="trust_score",
                    entity_id=updated_ts.id,
                    link="/trust-score",
                )
            except Exception:
                pass

        return updated_ts, True

    @classmethod
    def _build_factors(cls, ts: TrustScore) -> List[TrustScoreFactor]:
        return [
            TrustScoreFactor(
                name="Platform Verification",
                points=ts.verification_points,
                max_points=25,
                description="Identity, organization validation, and completed platform profile."
            ),
            TrustScoreFactor(
                name="Commitment Reliability",
                points=ts.commitments_points,
                max_points=35,
                description=f"Track record of fulfilled sponsorship agreements ({ts.completed_commitments_count} completed)."
            ),
            TrustScoreFactor(
                name="Milestone Reliability",
                points=ts.responsiveness_points,
                max_points=20,
                description=f"Verifiable progress milestones and evidence delivery ({ts.completed_milestones_count} verified)."
            ),
            TrustScoreFactor(
                name="Responsiveness & Activity",
                points=ts.activity_points,
                max_points=20,
                description="Timely response to sponsorship requests and regular platform updates."
            )
        ]

    @classmethod
    async def get_trust_breakdown(cls, db: AsyncSession, user_id: int) -> TrustScoreRead:
        """Full private breakdown including audit events for authenticated user."""
        ts = await cls.recalculate_trust_score(db, user_id)

        events_query = (
            select(TrustScoreEvent)
            .where(TrustScoreEvent.user_id == user_id)
            .order_by(TrustScoreEvent.created_at.desc())
            .limit(20)
        )
        events_result = await db.execute(events_query)
        events = events_result.scalars().all()

        factors = cls._build_factors(ts)

        return TrustScoreRead(
            id=ts.id,
            user_id=ts.user_id,
            score=ts.score,
            verification_points=ts.verification_points,
            commitments_points=ts.commitments_points,
            responsiveness_points=ts.responsiveness_points,
            activity_points=ts.activity_points,
            completed_commitments_count=ts.completed_commitments_count,
            cancelled_commitments_count=ts.cancelled_commitments_count,
            completed_milestones_count=ts.completed_milestones_count,
            avg_response_hours=ts.avg_response_hours,
            score_version=ts.score_version,
            last_calculated_at=ts.last_calculated_at,
            factors=factors,
            events=[TrustScoreEventRead.model_validate(e) for e in events],
        )

    @classmethod
    async def get_public_trust_breakdown(cls, db: AsyncSession, user_id: int) -> TrustScorePublicRead:
        """Safe public breakdown: strips raw event details, private notes, and counterparty data."""
        ts = await cls.recalculate_trust_score(db, user_id)
        factors = cls._build_factors(ts)

        return TrustScorePublicRead(
            id=ts.id,
            user_id=ts.user_id,
            score=ts.score,
            verification_points=ts.verification_points,
            commitments_points=ts.commitments_points,
            responsiveness_points=ts.responsiveness_points,
            activity_points=ts.activity_points,
            completed_commitments_count=ts.completed_commitments_count,
            completed_milestones_count=ts.completed_milestones_count,
            avg_response_hours=ts.avg_response_hours,
            score_version=ts.score_version,
            last_calculated_at=ts.last_calculated_at,
            factors=factors,
        )

    @classmethod
    async def get_trust_history(
        cls,
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> TrustScoreHistoryResponse:
        """Retrieves paginated audit log of trust events."""
        ts = await cls.get_or_create_trust_score(db, user_id)

        count_q = select(func.count(TrustScoreEvent.id)).where(TrustScoreEvent.user_id == user_id)
        total_events = await db.scalar(count_q) or 0

        events_q = (
            select(TrustScoreEvent)
            .where(TrustScoreEvent.user_id == user_id)
            .order_by(TrustScoreEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await db.execute(events_q)
        events = res.scalars().all()

        return TrustScoreHistoryResponse(
            user_id=user_id,
            current_score=ts.score,
            total_events=total_events,
            events=[TrustScoreEventRead.model_validate(e) for e in events],
        )
