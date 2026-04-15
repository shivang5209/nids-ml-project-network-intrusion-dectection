from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    prediction_id: int
    source_ip: str
    attack_type: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class AlertStatusUpdate(BaseModel):
    status: str

