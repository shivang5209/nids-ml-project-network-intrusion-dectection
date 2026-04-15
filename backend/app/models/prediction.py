from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    traffic_record_id: Mapped[int] = mapped_column(
        ForeignKey("traffic_records.id"),
        nullable=True,
    )
    predicted_label: Mapped[str] = mapped_column(String(32), nullable=False)
    attack_type: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), default="baseline-v1", nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    traffic_record = relationship("TrafficRecord", back_populates="predictions")
    alerts = relationship("Alert", back_populates="prediction")
