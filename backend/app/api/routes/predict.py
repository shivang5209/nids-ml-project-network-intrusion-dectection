from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, Prediction, TrafficRecord, User
from app.schemas.predict import (
    PredictRequest,
    PredictResponse,
    PredictionHistoryItem,
    PredictionHistoryResponse,
)
from app.services.model_service import map_severity, run_model_inference

router = APIRouter()


@router.get("/history", response_model=PredictionHistoryResponse)
def prediction_history(
    label: str | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionHistoryResponse:
    statement = select(Prediction)

    if label:
        statement = statement.where(Prediction.predicted_label == label.lower())
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Prediction.attack_type.ilike(pattern),
                Prediction.model_version.ilike(pattern),
                Prediction.predicted_label.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(
        statement.order_by(Prediction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PredictionHistoryResponse(
        items=[
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
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


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
