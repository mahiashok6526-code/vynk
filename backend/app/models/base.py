from datetime import datetime, timezone
from sqlalchemy import Column, DateTime


class TimestampMixin:
    """Reusable mixin providing created_at and updated_at timezone-aware timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
