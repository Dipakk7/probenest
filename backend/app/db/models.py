from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SystemMetadata(Base):
    """System metadata model for storing foundation information."""

    __tablename__ = "system_metadata"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )
