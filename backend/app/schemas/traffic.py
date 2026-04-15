from pydantic import BaseModel, Field


class TrafficIn(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str = Field(default="TCP")
    packet_count: int = Field(default=0, ge=0)
    byte_count: int = Field(default=0, ge=0)
    flow_duration: float = Field(default=0.0, ge=0.0)


class TrafficOut(TrafficIn):
    id: int

    class Config:
        from_attributes = True


class CaptureStartRequest(BaseModel):
    interface: str | None = None
    interval_seconds: int = Field(default=5, ge=1, le=60)


class CaptureStatusResponse(BaseModel):
    running: bool
    interface: str | None
    interval_seconds: int
    batches_processed: int
    last_batch_at: str | None
    last_error: str | None
    last_feature_snapshot: dict | None
