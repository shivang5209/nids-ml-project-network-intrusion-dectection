from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, User
from app.schemas.alerts import AlertOut, AlertStatusUpdate

router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AlertOut]:
    rows = db.scalars(select(Alert).order_by(Alert.id.desc()).limit(100)).all()
    return [AlertOut.model_validate(row) for row in rows]


@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertOut:
    alert = db.scalar(select(Alert).where(Alert.id == alert_id))
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.status
    if payload.status.lower() == "resolved":
        alert.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alert)
    return AlertOut.model_validate(alert)

