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

NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Normalize a raw network CSV into backend/data/nids_dataset.csv format."
    )
    parser.add_argument("input_csv", help="Path to the raw source CSV")
    parser.add_argument(
        "--format",
        choices=["auto", "nsl-kdd"],
        default="auto",
        help="Optional dataset format hint (default: auto)",
    )
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


def normalize_nsl_attack_type(value: object) -> str:
    text = str(value).strip().lower()
    if text == "normal":
        return "Normal"
    if any(token in text for token in ["neptune", "smurf", "back", "teardrop", "pod", "land"]):
        return "DDoS"
    if any(token in text for token in ["satan", "ipsweep", "nmap", "portsweep", "mscan", "saint"]):
        return "Probe"
    if any(token in text for token in ["guess_passwd", "ftp_write", "imap", "multihop", "phf", "spy", "warez", "warezclient"]):
        return "Credential Attack"
    if any(token in text for token in ["buffer_overflow", "rootkit", "perl", "loadmodule", "sqlattack", "xterm", "ps"]):
        return "Privilege Escalation"
    return text.replace("_", " ").title()


def normalize_nsl_kdd(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [str(column).strip().lower() for column in frame.columns]
    frame = frame.copy()
    frame.columns = columns

    if "protocol_type" not in frame.columns or "label" not in frame.columns:
        raise ValueError(
            "NSL-KDD input must include 'protocol_type' and 'label' columns."
        )

    if "src_bytes" not in frame.columns or "dst_bytes" not in frame.columns:
        raise ValueError(
            "NSL-KDD input must include 'src_bytes' and 'dst_bytes' columns."
        )

    packet_like_columns = [
        column
        for column in [
            "count",
            "srv_count",
            "dst_host_count",
            "dst_host_srv_count",
        ]
        if column in frame.columns
    ]

    output = pd.DataFrame()
    if packet_like_columns:
        output["packet_count"] = (
            frame[packet_like_columns]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
            .max(axis=1)
        )
    else:
        output["packet_count"] = 1

    output["byte_count"] = (
        pd.to_numeric(frame["src_bytes"], errors="coerce").fillna(0)
        + pd.to_numeric(frame["dst_bytes"], errors="coerce").fillna(0)
    )

    if "duration" in frame.columns:
        output["flow_duration"] = pd.to_numeric(frame["duration"], errors="coerce").fillna(0)
    else:
        output["flow_duration"] = 0

    output["protocol"] = frame["protocol_type"].map(normalize_protocol)
    output["label"] = frame["label"].map(normalize_label)
    output["attack_type"] = frame["label"].map(normalize_nsl_attack_type)

    return output[OUTPUT_COLUMNS].dropna()


def load_nsl_kdd_frame(input_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(input_path, header=None)
    column_count = frame.shape[1]

    if column_count == len(NSL_KDD_COLUMNS):
        frame.columns = NSL_KDD_COLUMNS
        return frame

    if column_count == len(NSL_KDD_COLUMNS) - 1:
        frame.columns = NSL_KDD_COLUMNS[:-1]
        return frame

    raise ValueError(
        f"Unexpected NSL-KDD column count: {column_count}. Expected 42 or 43 columns."
    )


def normalize_auto(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()

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

    return output[OUTPUT_COLUMNS].dropna()


def main():
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    if args.format == "nsl-kdd":
        frame = load_nsl_kdd_frame(input_path)
        output = normalize_nsl_kdd(frame)
    else:
        frame = pd.read_csv(input_path)
        output = normalize_auto(frame)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)

    print(f"Saved normalized dataset to {output_path}")
    print(f"Rows written: {len(output)}")


if __name__ == "__main__":
    main()
