from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TrafficRecord(Base):
    __tablename__ = "traffic_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_ip: Mapped[str] = mapped_column(String(64), nullable=False)
    destination_ip: Mapped[str] = mapped_column(String(64), nullable=False)
    protocol: Mapped[str] = mapped_column(String(32), nullable=False)
    packet_count: Mapped[int] = mapped_column(default=0, nullable=False)
    byte_count: Mapped[int] = mapped_column(default=0, nullable=False)
    flow_duration: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    predictions = relationship("Prediction", back_populates="traffic_record")

