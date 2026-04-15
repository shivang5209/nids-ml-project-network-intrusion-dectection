from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import TrafficRecord, User
from app.schemas.traffic import TrafficIn, TrafficOut

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

