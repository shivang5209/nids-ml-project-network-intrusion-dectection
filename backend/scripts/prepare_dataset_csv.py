from argparse import ArgumentParser
from pathlib import Path

import pandas as pd


OUTPUT_COLUMNS = [
    "packet_count",
    "byte_count",
    "flow_duration",
    "protocol",
    "label",
    "attack_type",
]


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Normalize a raw network CSV into backend/data/nids_dataset.csv format."
    )
    parser.add_argument("input_csv", help="Path to the raw source CSV")
    parser.add_argument(
        "--output",
        default="data/nids_dataset.csv",
        help="Output CSV path (default: data/nids_dataset.csv)",
    )
    return parser


def find_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    normalized = {column.strip().lower(): column for column in frame.columns}
    for alias in aliases:
        match = normalized.get(alias.strip().lower())
        if match:
            return match
    return None


def normalize_protocol(value: object) -> str:
    text = str(value).strip().upper()
    if text in {"6", "TCP"}:
        return "TCP"
    if text in {"17", "UDP"}:
        return "UDP"
    if text in {"1", "ICMP"}:
        return "ICMP"
    return text or "TCP"


def normalize_label(value: object) -> str:
    text = str(value).strip().lower()
    if text in {"normal", "benign", "safe"}:
        return "normal"
    return "malicious"


def normalize_attack_type(value: object) -> str:
    text = str(value).strip()
    return text if text else "Normal"


def main():
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    frame = pd.read_csv(input_path)

    packet_count_col = find_column(
        frame,
        [
            "packet_count",
            "total_packets",
            "tot_fwd_pkts",
            "tot fwd pkts",
        ],
    )
    packet_count_bwd_col = find_column(frame, ["tot_bwd_pkts", "tot bwd pkts"])

    byte_count_col = find_column(
        frame,
        [
            "byte_count",
            "total_bytes",
            "totlen_fwd_pkts",
            "totlen fwd pkts",
            "total_length_of_fwd_packets",
        ],
    )
    byte_count_bwd_col = find_column(
        frame,
        [
            "totlen_bwd_pkts",
            "totlen bwd pkts",
            "total_length_of_bwd_packets",
        ],
    )

    flow_duration_col = find_column(frame, ["flow_duration", "flow duration"])
    protocol_col = find_column(frame, ["protocol"])
    label_col = find_column(frame, ["label"])
    attack_type_col = find_column(frame, ["attack_type", "attack", "label"])

    missing = []
    if not packet_count_col and not (packet_count_col and packet_count_bwd_col):
        missing.append("packet_count or Tot Fwd/Bwd Pkts")
    if not byte_count_col and not (byte_count_col and byte_count_bwd_col):
        missing.append("byte_count or TotLen Fwd/Bwd Pkts")
    if not flow_duration_col:
        missing.append("flow_duration")
    if not protocol_col:
        missing.append("protocol")
    if not label_col:
        missing.append("label")

    if missing:
        raise ValueError(f"Could not map required columns: {missing}")

    output = pd.DataFrame()

    if packet_count_bwd_col:
        output["packet_count"] = (
            pd.to_numeric(frame[packet_count_col], errors="coerce").fillna(0)
            + pd.to_numeric(frame[packet_count_bwd_col], errors="coerce").fillna(0)
        )
    else:
        output["packet_count"] = pd.to_numeric(frame[packet_count_col], errors="coerce").fillna(0)

    if byte_count_bwd_col:
        output["byte_count"] = (
            pd.to_numeric(frame[byte_count_col], errors="coerce").fillna(0)
            + pd.to_numeric(frame[byte_count_bwd_col], errors="coerce").fillna(0)
        )
    else:
        output["byte_count"] = pd.to_numeric(frame[byte_count_col], errors="coerce").fillna(0)

    output["flow_duration"] = pd.to_numeric(frame[flow_duration_col], errors="coerce").fillna(0)
    output["protocol"] = frame[protocol_col].map(normalize_protocol)
    output["label"] = frame[label_col].map(normalize_label)

    if attack_type_col:
        output["attack_type"] = frame[attack_type_col].map(normalize_attack_type)
    else:
        output["attack_type"] = output["label"].map(
            lambda label: "Normal" if label == "normal" else "Unknown Attack"
        )

    output = output[OUTPUT_COLUMNS].dropna()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)

    print(f"Saved normalized dataset to {output_path}")
    print(f"Rows written: {len(output)}")


if __name__ == "__main__":
    main()
