# NIDS Backend

FastAPI backend for the Network Intrusion Detection System project.

## Features

- JWT login and profile endpoints
- Traffic ingestion and live feed endpoints
- Trained-model prediction endpoint with heuristic fallback
- Alerts list and status update
- Dashboard summary and daily report endpoints
- Auto-bootstrap admin user and DB tables on startup

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional:

1. Copy `.env.example` to `.env`.
2. Set `SECRET_KEY` and admin credentials.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Train Demo Model

If no model artifact exists, backend prediction falls back to the heuristic engine.

To train and save a demo Random Forest model:

```bash
python scripts/train_demo_model.py
```

This writes:

- `backend/artifacts/nids_model.joblib`

## Train From Real CSV Dataset

Place a CSV file at:

- `backend/data/nids_dataset.csv`

Minimum required columns:

- `packet_count`
- `byte_count`
- `flow_duration`
- `protocol` or `protocol_code`
- `label`
- `attack_type`

Example labels:

- `normal`
- `malicious`

Example attack types:

- `Normal`
- `DDoS`
- `Probe`
- `Port Scan`

Run training:

```bash
python scripts/train_from_csv.py
```

This will overwrite the active model artifact at:

- `backend/artifacts/nids_model.joblib`

## Prepare a Real Public Dataset

If you want a stronger academic dataset than the small demo CSV, use an **NSL-KDD** style CSV and normalize it first:

```bash
python scripts/prepare_dataset_csv.py "path/to/nsl_kdd.csv" --format nsl-kdd
python scripts/train_from_csv.py
```

This converts the raw file into:

- `backend/data/nids_dataset.csv`

and then retrains the active model artifact with real rows.

## Default Admin

- Email: `admin@nidsdemo.com`
- Password: `admin123`

Change these in `.env` before production/demo use.
