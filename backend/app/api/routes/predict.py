from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, Prediction, TrafficRecord, User
from app.schemas.predict import PredictRequest, PredictResponse, PredictionHistoryItem
from app.services.model_service import map_severity, run_model_inference

router = APIRouter()


@router.get("/history", response_model=list[PredictionHistoryItem])
def prediction_history(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PredictionHistoryItem]:
    rows = db.scalars(
        select(Prediction).order_by(Prediction.id.desc()).limit(100)
    ).all()
    return [
        PredictionHistoryItem(
            id=row.id,
            traffic_record_id=row.traffic_record_id,
            predicted_label=row.predicted_label,
            attack_type=row.attack_type,
            confidence_score=row.confidence_score,
            model_version=row.model_version,
            predicted_at=row.predicted_at.isoformat(),
        )
        for row in rows
    ]


@router.post("", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictResponse:
    traffic_record = TrafficRecord(**payload.model_dump())
    db.add(traffic_record)
    db.flush()

    model_output = run_model_inference(payload)
    prediction = Prediction(
        traffic_record_id=traffic_record.id,
        predicted_label=model_output.label,
        attack_type=model_output.attack_type,
        confidence_score=model_output.confidence,
        model_version=model_output.model_version,
    )
    db.add(prediction)
    db.flush()

    alert_created = False
    if model_output.label == "malicious":
        alert = Alert(
            prediction_id=prediction.id,
            source_ip=payload.source_ip,
            attack_type=model_output.attack_type,
            severity=map_severity(model_output.attack_type),
        )
        db.add(alert)
        alert_created = True

    db.commit()

    return PredictResponse(
        prediction_id=prediction.id,
        label=model_output.label,
        attack_type=model_output.attack_type,
        confidence=model_output.confidence,
        alert_created=alert_created,
    )
