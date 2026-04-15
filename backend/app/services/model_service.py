from dataclasses import dataclass

from app.schemas.predict import PredictRequest


@dataclass
class ModelOutput:
    label: str
    attack_type: str
    confidence: float
    model_version: str


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

