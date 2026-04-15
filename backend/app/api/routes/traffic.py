from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import TrafficRecord, User
from app.schemas.traffic import (
    CaptureStartRequest,
    CaptureStatusResponse,
    TrafficIn,
    TrafficOut,
)
from app.services.live_capture_service import live_capture_manager

router = APIRouter()


@router.post("/upload", response_model=TrafficOut)
def upload_traffic(
    payload: TrafficIn,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrafficOut:
    record = TrafficRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return TrafficOut.model_validate(record)


@router.get("/live", response_model=list[TrafficOut])
def live_traffic(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TrafficOut]:
    records = db.scalars(
        select(TrafficRecord).order_by(TrafficRecord.id.desc()).limit(25)
    ).all()
    return [TrafficOut.model_validate(item) for item in records]


@router.post("/capture/start", response_model=CaptureStatusResponse)
def start_live_capture(
    payload: CaptureStartRequest,
    _: User = Depends(get_current_user),
) -> CaptureStatusResponse:
    state = live_capture_manager.start(
        interface=payload.interface,
        interval_seconds=payload.interval_seconds,
    )
    return CaptureStatusResponse.model_validate(state.__dict__)


@router.post("/capture/stop", response_model=CaptureStatusResponse)
def stop_live_capture(
    _: User = Depends(get_current_user),
) -> CaptureStatusResponse:
    state = live_capture_manager.stop()
    return CaptureStatusResponse.model_validate(state.__dict__)


@router.get("/capture/status", response_model=CaptureStatusResponse)
def live_capture_status(
    _: User = Depends(get_current_user),
) -> CaptureStatusResponse:
    state = live_capture_manager.status()
    return CaptureStatusResponse.model_validate(state.__dict__)
