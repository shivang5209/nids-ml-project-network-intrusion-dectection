from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, Prediction, TrafficRecord, User
from app.schemas.dashboard import DashboardSummary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def summary(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    total_traffic = db.scalar(select(func.count()).select_from(TrafficRecord)) or 0
    total_predictions = db.scalar(select(func.count()).select_from(Prediction)) or 0
    total_alerts = db.scalar(select(func.count()).select_from(Alert)) or 0
    open_alerts = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status != "Resolved")
    ) or 0
    malicious_predictions = db.scalar(
        select(func.count())
        .select_from(Prediction)
        .where(Prediction.predicted_label == "malicious")
    ) or 0

    return DashboardSummary(
        total_traffic_records=total_traffic,
        total_predictions=total_predictions,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        malicious_predictions=malicious_predictions,
    )

