from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, Prediction, User

router = APIRouter()


@router.get("/daily")
def daily_report(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    recent_predictions = db.scalars(
        select(Prediction).order_by(Prediction.id.desc()).limit(100)
    ).all()
    recent_alerts = db.scalars(select(Alert).order_by(Alert.id.desc()).limit(100)).all()

    labels = Counter(item.predicted_label for item in recent_predictions)
    attacks = Counter(item.attack_type for item in recent_predictions)
    severities = Counter(item.severity for item in recent_alerts)

    return {
        "prediction_count": len(recent_predictions),
        "alert_count": len(recent_alerts),
        "labels": dict(labels),
        "attack_types": dict(attacks),
        "severities": dict(severities),
    }

