import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SystemMetadata(Base):
    """System metadata model for storing foundation information."""

    __tablename__ = "system_metadata"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class EvaluationRunModel(Base):
    """SQLAlchemy model for evaluation runs."""

    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)

    results: Mapped[list["EvaluationResultModel"]] = relationship(
        "EvaluationResultModel", back_populates="run", cascade="all, delete-orphan"
    )


class EvaluationResultModel(Base):
    """SQLAlchemy model for individual evaluation case outcomes."""

    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True
    )
    test_id: Mapped[str] = mapped_column(String(128), nullable=False)
    evaluator: Mapped[str] = mapped_column(String(128), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str | None] = mapped_column(String(32), nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")

    run: Mapped["EvaluationRunModel"] = relationship("EvaluationRunModel", back_populates="results")

    @property
    def evidence(self) -> dict[str, Any]:
        """Deserialize stored JSON evidence into dict."""
        try:
            return json.loads(self.evidence_json)
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}

    @evidence.setter
    def evidence(self, value: dict[str, Any]) -> None:
        """Serialize dict evidence into JSON string."""
        self.evidence_json = json.dumps(value or {})
