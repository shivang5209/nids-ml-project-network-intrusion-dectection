from sqlalchemy.orm import Session

from app.models import Alert, Prediction, TrafficRecord
from app.schemas.predict import PredictRequest
from app.services.model_service import map_severity, run_model_inference


def persist_prediction(payload: PredictRequest, db: Session) -> dict:
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

    return {
        "prediction_id": prediction.id,
        "label": model_output.label,
        "attack_type": model_output.attack_type,
        "confidence": model_output.confidence,
        "alert_created": alert_created,
    }
