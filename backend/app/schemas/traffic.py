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

