from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATASET_PATH = Path("data/nids_dataset.csv")
ARTIFACT_PATH = Path("artifacts/nids_model.joblib")

FEATURE_COLUMNS = [
    "packet_count",
    "byte_count",
    "flow_duration",
    "protocol_code",
]


def encode_protocol_column(frame: pd.DataFrame) -> pd.DataFrame:
    protocol_map = {"TCP": 0, "UDP": 1, "ICMP": 2}

    if "protocol_code" in frame.columns:
        return frame

    if "protocol" not in frame.columns:
        raise ValueError("Dataset must include either 'protocol' or 'protocol_code' column.")

    frame = frame.copy()
    frame["protocol_code"] = (
        frame["protocol"].astype(str).str.upper().map(protocol_map).fillna(3).astype(int)
    )
    return frame


def normalize_label(value: str) -> str:
    text = str(value).strip().lower()
    if text in {"normal", "benign", "safe"}:
        return "normal"
    return "malicious"


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            "Dataset file not found. Place your CSV at backend/data/nids_dataset.csv"
        )

    frame = pd.read_csv(DATASET_PATH)
    frame = encode_protocol_column(frame)

    required_columns = set(FEATURE_COLUMNS + ["label", "attack_type"])
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Dataset missing required columns: {sorted(missing_columns)}")

    frame = frame.dropna(subset=FEATURE_COLUMNS + ["label", "attack_type"]).copy()
    frame["label"] = frame["label"].map(normalize_label)
    frame["attack_type"] = frame["attack_type"].astype(str)

    features = frame[FEATURE_COLUMNS].astype(float)

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(frame["label"])

    attack_encoder = LabelEncoder()
    encoded_attacks = attack_encoder.fit_transform(frame["attack_type"])

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        encoded_labels,
        test_size=0.2,
        random_state=42,
        stratify=encoded_labels,
    )

    model = RandomForestClassifier(
        n_estimators=220,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    attack_model = RandomForestClassifier(
        n_estimators=180,
        random_state=42,
        class_weight="balanced",
    )
    attack_model.fit(features, encoded_attacks)

    accuracy = float(model.score(x_test, y_test))

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "attack_model": attack_model,
            "label_encoder": label_encoder,
            "attack_encoder": attack_encoder,
            "model_version": "csv-rf-v1",
            "accuracy": accuracy,
            "feature_columns": FEATURE_COLUMNS,
        },
        ARTIFACT_PATH,
    )

    print(f"Saved trained artifact to {ARTIFACT_PATH}")
    print(f"Validation accuracy: {accuracy:.4f}")
    print(f"Rows used: {len(frame)}")


if __name__ == "__main__":
    main()
