from collections import Counter
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Alert, Prediction, User
from app.services.model_service import load_model_artifact

router = APIRouter()


def _csv_response(filename: str, fieldnames: list[str], rows: list[dict]) -> StreamingResponse:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _apply_alert_filters(statement, severity: str | None, status: str | None, q: str | None):
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
    return statement


def _apply_prediction_filters(statement, label: str | None, q: str | None):
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
    return statement


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


@router.get("/analytics")
def analytics_report(
    hours: int = Query(default=12, ge=6, le=72),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    recent_predictions = db.scalars(
        select(Prediction).order_by(Prediction.predicted_at.desc()).limit(max(hours * 20, 250))
    ).all()
    recent_alerts = db.scalars(
        select(Alert).order_by(Alert.created_at.desc()).limit(max(hours * 20, 250))
    ).all()

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    timeline_keys = [now - timedelta(hours=index) for index in range(hours - 1, -1, -1)]
    timeline_counts = {
        bucket: {"count": 0, "malicious_count": 0} for bucket in timeline_keys
    }

    for item in recent_predictions:
        predicted_at = item.predicted_at
        if predicted_at.tzinfo is None:
            predicted_at = predicted_at.replace(tzinfo=timezone.utc)
        bucket = predicted_at.astimezone(timezone.utc).replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        if bucket in timeline_counts:
            timeline_counts[bucket]["count"] += 1
            if item.predicted_label == "malicious":
                timeline_counts[bucket]["malicious_count"] += 1

    attack_distribution = Counter(
        item.attack_type for item in recent_predictions if item.predicted_label == "malicious"
    )
    severity_distribution = Counter(item.severity for item in recent_alerts)

    return {
        "timeline": [
            {
                "hour": bucket.isoformat(),
                "label": bucket.strftime("%H:%M"),
                "count": timeline_counts[bucket]["count"],
                "malicious_count": timeline_counts[bucket]["malicious_count"],
            }
            for bucket in timeline_keys
        ],
        "attack_distribution": dict(attack_distribution),
        "severity_distribution": dict(severity_distribution),
        "malicious_prediction_count": sum(attack_distribution.values()),
        "window_hours": hours,
    }


@router.get("/export/alerts")
def export_alerts_report(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    statement = _apply_alert_filters(select(Alert), severity, status, q)
    rows = db.scalars(statement.order_by(Alert.id.desc()).limit(500)).all()
    csv_rows = [
        {
            "id": row.id,
            "source_ip": row.source_ip,
            "attack_type": row.attack_type,
            "severity": row.severity,
            "status": row.status,
            "created_at": row.created_at.isoformat(),
            "resolved_at": row.resolved_at.isoformat() if row.resolved_at else "",
        }
        for row in rows
    ]
    return _csv_response(
        "nids-alerts-report.csv",
        ["id", "source_ip", "attack_type", "severity", "status", "created_at", "resolved_at"],
        csv_rows,
    )


@router.get("/export/predictions")
def export_predictions_report(
    label: str | None = Query(default=None),
    q: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    statement = _apply_prediction_filters(select(Prediction), label, q)
    rows = db.scalars(statement.order_by(Prediction.id.desc()).limit(500)).all()
    csv_rows = [
        {
            "id": row.id,
            "traffic_record_id": row.traffic_record_id,
            "predicted_label": row.predicted_label,
            "attack_type": row.attack_type,
            "confidence_score": row.confidence_score,
            "model_version": row.model_version,
            "predicted_at": row.predicted_at.isoformat(),
        }
        for row in rows
    ]
    return _csv_response(
        "nids-predictions-report.csv",
        [
            "id",
            "traffic_record_id",
            "predicted_label",
            "attack_type",
            "confidence_score",
            "model_version",
            "predicted_at",
        ],
        csv_rows,
    )


@router.get("/export/analytics")
def export_analytics_report(
    hours: int = Query(default=12, ge=6, le=72),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    analytics = analytics_report(hours=hours, _=_, db=db)
    csv_rows = [
        {
            "window_hours": analytics["window_hours"],
            "hour": item["hour"],
            "label": item["label"],
            "prediction_count": item["count"],
            "malicious_count": item["malicious_count"],
        }
        for item in analytics["timeline"]
    ]
    return _csv_response(
        f"nids-analytics-{hours}h.csv",
        ["window_hours", "hour", "label", "prediction_count", "malicious_count"],
        csv_rows,
    )


@router.get("/model-evaluation")
def model_evaluation_report(
    _: User = Depends(get_current_user),
) -> dict:
    artifact = load_model_artifact()
    if not artifact:
        return {
            "available": False,
            "model_version": "heuristic-v1",
            "evaluation": None,
        }

    evaluation = artifact.get("evaluation") or {
        "accuracy": artifact.get("accuracy"),
        "precision": None,
        "recall": None,
        "f1_score": None,
        "true_negative": None,
        "false_positive": None,
        "false_negative": None,
        "true_positive": None,
        "dataset_rows": None,
        "evaluation_samples": None,
    }
    return {
        "available": True,
        "model_version": artifact.get("model_version", "trained-v1"),
        "evaluation": evaluation,
    }
