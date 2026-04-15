# Dataset Preparation

The backend trainer expects a CSV at:

- `backend/data/nids_dataset.csv`

## Required columns

- `packet_count`
- `byte_count`
- `flow_duration`
- `protocol`
- `label`
- `attack_type`

## Quickest path

If you already have a raw CSV from a dataset such as CIC-IDS2017 or a custom export, run:

```powershell
cd D:\ml-project\backend
python scripts\prepare_dataset_csv.py "path\to\raw_dataset.csv"
```

## Recommended Real Dataset Path

The easiest real public dataset format to adapt into this project is **NSL-KDD**.

If you convert the NSL-KDD data file into CSV first, run:

```powershell
cd D:\ml-project\backend
python scripts\prepare_dataset_csv.py "path\to\nsl_kdd.csv" --format nsl-kdd
```

This maps:

- `protocol_type` -> `protocol`
- `src_bytes + dst_bytes` -> `byte_count`
- `duration` -> `flow_duration`
- one of `count`, `srv_count`, `dst_host_count`, `dst_host_srv_count` -> `packet_count`
- `label` -> `label`
- `label` -> grouped `attack_type`

Grouped attack types include:

- `Normal`
- `DDoS`
- `Probe`
- `Credential Attack`
- `Privilege Escalation`

That writes:

- `backend/data/nids_dataset.csv`

Then train:

```powershell
python scripts\train_from_csv.py
```

## Supported raw column mappings

The normalizer can map these common source columns:

- `Protocol` -> `protocol`
- `Flow Duration` -> `flow_duration`
- `Tot Fwd Pkts` + `Tot Bwd Pkts` -> `packet_count`
- `TotLen Fwd Pkts` + `TotLen Bwd Pkts` -> `byte_count`
- `Label` -> `label`

It also supports:

- `NSL-KDD` style CSV input through `--format nsl-kdd`

If your raw dataset already has:

- `packet_count`
- `byte_count`
- `flow_duration`
- `protocol`
- `label`
- `attack_type`

then you can place it directly as `backend/data/nids_dataset.csv` and skip the prep script.

## Example normalized rows

See:

- [nids_dataset_template.csv](D:/ml-project/backend/data/nids_dataset_template.csv)

## Label rules

- `normal`, `benign`, `safe` become `normal`
- everything else becomes `malicious`

For `attack_type`, keep values such as:

- `Normal`
- `DDoS`
- `Probe`
- `Port Scan`
- `Botnet`
