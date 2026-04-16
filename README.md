# Network Intrusion Detection System (NIDS) - Full Stack ML Project

A machine learning-powered web application for network intrusion detection that classifies traffic features as `normal` or `malicious`, stores predictions and alerts, and provides a monitoring dashboard with analytics, exports, and live capture control.

## Project Overview

This project demonstrates an end-to-end ML + web pipeline for intrusion detection:

- Backend: FastAPI REST API with ML inference and database persistence
- Frontend: React + Vite dashboard
- ML Model: Random Forest classifier with protocol/flow feature inputs
- Dataset Pipeline: CSV normalization (including NSL-KDD adaptation) and model retraining
- Live Capture (MVP): Local packet sniffing with Scapy and automated prediction ingestion

## Key Features

- Real-time-ish prediction via API and dashboard inference form
- Automatic alert generation for malicious predictions
- Alert workflow with status updates (including resolve)
- Prediction history with server-side filtering and pagination
- Analytics timeline with selectable window and hover details
- CSV exports for alerts, predictions, and analytics
- Model evaluation panel (accuracy, precision, recall, F1, TP/TN/FP/FN)
- Live capture controls (`start`, `stop`, `status`) from UI and API

## Project Structure

```text
ml-project/
|-- backend/
|   |-- app/
|   |   |-- api/routes/
|   |   |   |-- auth.py
|   |   |   |-- dashboard.py
|   |   |   |-- traffic.py
|   |   |   |-- predict.py
|   |   |   |-- alerts.py
|   |   |   |-- reports.py
|   |   |   `-- health.py
|   |   |-- services/
|   |   |   |-- model_service.py
|   |   |   |-- prediction_pipeline.py
|   |   |   `-- live_capture_service.py
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- main.py
|   |-- scripts/
|   |   |-- train_demo_model.py
|   |   |-- train_from_csv.py
|   |   `-- prepare_dataset_csv.py
|   |-- data/
|   |   `-- nids_dataset.csv
|   |-- artifacts/
|   |   `-- nids_model.joblib
|   |-- requirements.txt
|   |-- DATASET_PREP.md
|   `-- README.md
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- api.js
|   |   |-- styles.css
|   |   `-- data.js
|   |-- package.json
|   `-- vite.config.js
|-- network_intrusion_detection_research.md
|-- nids_full_project_execution_flow.md
`-- README.md
```

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, PyJWT
- Frontend: React, Vite
- ML: scikit-learn, pandas, numpy, joblib
- Capture: Scapy
- Database: SQLite (default), configurable via environment

## Installation and Setup

### Prerequisites

- Python 3.10+ recommended
- Node.js 18+ recommended
- npm
- (For live capture on Windows) Npcap installed

### 1. Backend dependencies

```powershell
cd D:\ml-project\backend
python -m pip install -r requirements.txt
```

### 2. Frontend dependencies

```powershell
cd D:\ml-project\frontend
npm install
```

## Model Training

### Option A: Train from prepared dataset

```powershell
cd D:\ml-project\backend
python scripts\train_from_csv.py
```

Expected output (example):

```text
Saved trained artifact to artifacts\nids_model.joblib
Validation accuracy: 0.9729
Rows used: 125973
```

### Option B: Prepare NSL-KDD raw file and train

```powershell
cd D:\ml-project\backend
python scripts\prepare_dataset_csv.py "data\KDDTrain+.txt" --format nsl-kdd
python scripts\train_from_csv.py
```

### Option C: Demo synthetic training

```powershell
cd D:\ml-project\backend
python scripts\train_demo_model.py
```

## Running the Application

### Terminal 1 - Start Backend

```powershell
cd D:\ml-project\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 - Start Frontend

```powershell
cd D:\ml-project\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Access URLs

- Frontend: `http://127.0.0.1:5173`
- Backend docs (Swagger): `http://127.0.0.1:8000/docs`
- Backend health: `http://127.0.0.1:8000/health`

Default login:

- Email: `admin@nidsdemo.com`
- Password: `admin123`

## How to Use

1. Login from frontend.
2. Use `Inference Lab` to submit traffic features.
3. Check prediction label/confidence and alert creation.
4. Review `Alert Queue` and resolve incidents.
5. Track `Prediction History` and `Traffic Timeline`.
6. Use filters and pagination for data review.
7. Export CSV reports (alerts, predictions, analytics).

## Live Capture (MVP)

This project includes a first live capture pipeline:

- Sniffs local IP packets in timed windows
- Aggregates packets into model input features
- Persists predictions and alerts automatically

API endpoints:

- `POST /traffic/capture/start`
- `GET /traffic/capture/status`
- `POST /traffic/capture/stop`

Example start request:

```json
{
  "interface": null,
  "interval_seconds": 5
}
```

Important notes:

- Windows typically requires Npcap for packet capture.
- Capture may require running backend with elevated permissions.
- If capture fails, check `last_error` from capture status endpoint or dashboard.

## Main API Endpoints

- Auth:
  - `POST /auth/login`
  - `GET /auth/profile`
- Dashboard:
  - `GET /dashboard/summary`
- Traffic:
  - `GET /traffic/live`
  - `POST /traffic/upload`
  - `POST /traffic/capture/start`
  - `GET /traffic/capture/status`
  - `POST /traffic/capture/stop`
- Prediction:
  - `POST /predict`
  - `GET /predict/history`
- Alerts:
  - `GET /alerts`
  - `PATCH /alerts/{alert_id}`
- Reports:
  - `GET /reports/daily`
  - `GET /reports/analytics`
  - `GET /reports/model-evaluation`
  - `GET /reports/export/alerts`
  - `GET /reports/export/predictions`
  - `GET /reports/export/analytics`

## Model Evaluation and Metrics

The trained artifact stores evaluation metrics surfaced in the dashboard:

- Accuracy
- Precision
- Recall
- F1 Score
- True Positive / True Negative
- False Positive / False Negative
- Dataset and evaluation sample counts

## Troubleshooting

### `Capture Error: Scapy unavailable: No module named 'scapy'`

```powershell
cd D:\ml-project\backend
python -m pip install -r requirements.txt
```

### Capture fails on Windows

- Install Npcap from `https://npcap.com/#download`
- Restart backend after installation
- Try running terminal as Administrator

### Backend not reachable from frontend

- Confirm backend is running on port `8000`
- Confirm frontend uses `http://127.0.0.1:8000` (default in `api.js`)
- Check browser console and backend terminal logs

### Model files missing or invalid

```powershell
cd D:\ml-project\backend
python scripts\train_from_csv.py
```

## Security Notes

- Current setup is development-focused.
- Default admin credentials should be overridden for real deployment.
- Use `.env`-based secrets and stricter CORS/auth hardening before production.
- Live capture endpoints should be restricted in production environments.

## Current Status

Current build is a strong academic prototype with:

- end-to-end ML inference flow
- integrated frontend/backend/data pipeline
- analytics + exports + pagination
- model evaluation visibility
- first practical live-capture ingestion path

## Recommended Next Enhancements

- Add role-based authorization for capture and admin actions
- Add queue/worker pipeline for higher traffic throughput
- Add persistent audit logs and better observability
- Add deployment target (Docker/VPS/cloud) and production config
- Expand dataset diversity and periodic retraining workflow
