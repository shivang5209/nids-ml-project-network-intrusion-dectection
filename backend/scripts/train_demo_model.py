from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

ARTIFACT_PATH = Path("artifacts/nids_model.joblib")


def generate_samples(sample_count: int = 2400, seed: int = 42):
    rng = np.random.default_rng(seed)

    packet_count = rng.integers(20, 2500, sample_count)
    byte_count = rng.integers(1000, 1_500_000, sample_count)
    flow_duration = rng.uniform(0.01, 9.0, sample_count)
    protocol_code = rng.integers(0, 3, sample_count)

    features = np.column_stack(
        [packet_count, byte_count, flow_duration, protocol_code]
    ).astype(float)

    labels = []
    attack_types = []

    for packets, bytes_, duration, proto in features:
        risk_score = 0
        if proto == 2:
            risk_score += 1
        if packets > 1500:
            risk_score += 1
        if bytes_ > 800_000:
            risk_score += 1
        if duration < 0.2 and packets > 400:
            risk_score += 1

        if risk_score >= 3:
            labels.append("malicious")
            attack_types.append("DDoS")
        elif risk_score == 2:
            labels.append("malicious")
            attack_types.append("Probe")
        else:
            labels.append("normal")
            attack_types.append("Normal")

    return features, np.array(labels), np.array(attack_types)


def main():
    features, labels, attack_types = generate_samples()

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    attack_encoder = LabelEncoder()
    encoded_attacks = attack_encoder.fit_transform(attack_types)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        encoded_labels,
        test_size=0.2,
        random_state=42,
        stratify=encoded_labels,
    )

    model = RandomForestClassifier(
        n_estimators=180,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    attack_model = RandomForestClassifier(
        n_estimators=120,
        random_state=42,
        class_weight="balanced",
    )
    attack_model.fit(features, encoded_attacks)

    predicted_labels = model.predict(x_test)
    accuracy = float(model.score(x_test, y_test))
    precision, recall, f1_score, _ = precision_recall_fscore_support(
        y_test,
        predicted_labels,
        average="binary",
        zero_division=0,
    )
    tn, fp, fn, tp = confusion_matrix(y_test, predicted_labels).ravel()
    evaluation = {
        "accuracy": accuracy,
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1_score),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "dataset_rows": int(len(labels)),
        "evaluation_samples": int(len(y_test)),
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "attack_model": attack_model,
            "label_encoder": label_encoder,
            "attack_encoder": attack_encoder,
            "model_version": "demo-rf-v1",
            "accuracy": accuracy,
            "evaluation": evaluation,
        },
        ARTIFACT_PATH,
    )

    print(f"Saved model artifact to {ARTIFACT_PATH}")
    print(f"Validation accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    main()
