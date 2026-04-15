from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, User
from app.schemas.alerts import AlertListResponse, AlertOut, AlertStatusUpdate

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    statement = select(Alert)

    if severity:
        statement = statement.where(Alert.severity == severity.lower())
    if status:
        statement = statement.where(Alert.status.ilike(status))
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Alert.source_ip.ilike(pattern),
                Alert.attack_type.ilike(pattern),
                Alert.status.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(
        statement.order_by(Alert.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return AlertListResponse(
        items=[AlertOut.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


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
