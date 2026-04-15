from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np

from app.core.config import settings
from app.schemas.predict import PredictRequest


@dataclass
class ModelOutput:
    label: str
    attack_type: str
    confidence: float
    model_version: str


def build_feature_vector(payload: PredictRequest) -> np.ndarray:
    protocol_map = {"TCP": 0, "UDP": 1, "ICMP": 2}
    return np.array(
        [
            payload.packet_count,
            payload.byte_count,
            payload.flow_duration,
            protocol_map.get(payload.protocol.upper(), 3),
        ],
        dtype=float,
    ).reshape(1, -1)


def load_trained_model() -> tuple[object, dict] | tuple[None, None]:
    artifact_path = Path(settings.model_artifact_path)
    if not artifact_path.exists():
        return None, None

    artifact = joblib.load(artifact_path)
    return artifact.get("model"), artifact


def load_model_artifact() -> dict | None:
    artifact_path = Path(settings.model_artifact_path)
    if not artifact_path.exists():
        return None
    return joblib.load(artifact_path)


def run_baseline_inference(payload: PredictRequest) -> ModelOutput:
    score = 0

    if payload.protocol.upper() == "ICMP":
        score += 1
    if payload.packet_count > 1500:
        score += 1
    if payload.byte_count > 800_000:
        score += 1
    if payload.flow_duration < 0.2 and payload.packet_count > 400:
        score += 1

    if score >= 3:
        return ModelOutput(
            label="malicious",
            attack_type="DDoS",
            confidence=0.93,
            model_version="heuristic-v1",
        )
    if score == 2:
        return ModelOutput(
            label="malicious",
            attack_type="Probe",
            confidence=0.79,
            model_version="heuristic-v1",
        )

    return ModelOutput(
        label="normal",
        attack_type="Normal",
        confidence=0.96,
        model_version="heuristic-v1",
    )


def run_model_inference(payload: PredictRequest) -> ModelOutput:
    model, artifact = load_trained_model()
    if model is None or artifact is None:
        return run_baseline_inference(payload)

    features = build_feature_vector(payload)
    label_encoder = artifact["label_encoder"]
    attack_encoder = artifact["attack_encoder"]
    probability = model.predict_proba(features)[0]
    prediction_index = int(np.argmax(probability))
    confidence = float(probability[prediction_index])

    label = label_encoder.inverse_transform([prediction_index])[0]

    attack_model = artifact.get("attack_model")
    if label == "normal":
        attack_type = "Normal"
    elif attack_model is not None:
        attack_prediction = attack_model.predict(features)[0]
        attack_type = attack_encoder.inverse_transform([attack_prediction])[0]
    else:
        attack_type = "Probe"

    return ModelOutput(
        label=label,
        attack_type=attack_type,
        confidence=confidence,
        model_version=artifact.get("model_version", "trained-v1"),
    )


def map_severity(attack_type: str) -> str:
    mapping = {
        "DDoS": "critical",
        "Botnet": "critical",
        "Ransomware": "critical",
        "Probe": "high",
        "Port Scan": "medium",
        "Normal": "low",
    }
    return mapping.get(attack_type, "medium")
