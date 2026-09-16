from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.trust import TrustScore, TrustScoreEvent
from app.models.user import User
from app.schemas.trust import TrustScoreRead, TrustScoreFactor, TrustScoreEventRead


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
                verification_points=0,
                commitments_points=20,
                responsiveness_points=15,
                activity_points=15,
            )
            db.add(ts)
            await db.commit()
            await db.refresh(ts)
        return ts

    @classmethod
    async def get_trust_breakdown(cls, db: AsyncSession, user_id: int) -> TrustScoreRead:
        ts = await cls.get_or_create_trust_score(db, user_id)

        # Fetch recent trust events
        events_query = (
            select(TrustScoreEvent)
            .where(TrustScoreEvent.user_id == user_id)
            .order_by(TrustScoreEvent.created_at.desc())
            .limit(10)
        )
        events_result = await db.execute(events_query)
        events = events_result.scalars().all()

        factors = [
            TrustScoreFactor(
                name="Platform Verification",
                points=ts.verification_points,
                max_points=25,
                description="Identity, organization validation, and background confirmation."
            ),
            TrustScoreFactor(
                name="Commitment Reliability",
                points=ts.commitments_points,
                max_points=35,
                description=f"Track record of fulfilled sponsorship agreements ({ts.completed_commitments_count} completed)."
            ),
            TrustScoreFactor(
                name="Communication Responsiveness",
                points=ts.responsiveness_points,
                max_points=20,
                description=f"Average response time (~{ts.avg_response_hours}h) and message inquiry fulfillment."
            ),
            TrustScoreFactor(
                name="Community Activity & Updates",
                points=ts.activity_points,
                max_points=20,
                description="Project development milestones, transparent reporting, and engagement."
            )
        ]

        total_score = min(100, max(0, (
            ts.verification_points +
            ts.commitments_points +
            ts.responsiveness_points +
            ts.activity_points
        )))

        if total_score != ts.score:
            ts.score = total_score
            ts.last_calculated_at = datetime.now(timezone.utc)
            await db.commit()

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
            avg_response_hours=ts.avg_response_hours,
            last_calculated_at=ts.last_calculated_at,
            factors=factors,
            events=[TrustScoreEventRead.model_validate(e) for e in events],
        )

    @classmethod
    async def record_event(
        cls,
        db: AsyncSession,
        user_id: int,
        event_type: str,
        impact: int,
        reason: str
    ):
        event = TrustScoreEvent(
            user_id=user_id,
            event_type=event_type,
            impact=impact,
            reason=reason,
        )
        db.add(event)
        ts = await cls.get_or_create_trust_score(db, user_id)
        # Update category points depending on event type
        if "verif" in event_type:
            ts.verification_points = min(25, max(0, ts.verification_points + impact))
        elif "commit" in event_type:
            ts.commitments_points = min(35, max(0, ts.commitments_points + impact))
            if impact > 0:
                ts.completed_commitments_count += 1
            else:
                ts.cancelled_commitments_count += 1
        elif "response" in event_type:
            ts.responsiveness_points = min(20, max(0, ts.responsiveness_points + impact))
        else:
            ts.activity_points = min(20, max(0, ts.activity_points + impact))

        ts.score = min(100, max(0, (
            ts.verification_points +
            ts.commitments_points +
            ts.responsiveness_points +
            ts.activity_points
        )))
        ts.last_calculated_at = datetime.now(timezone.utc)
        await db.commit()
