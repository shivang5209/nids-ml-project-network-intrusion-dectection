# NIDS ML Project

This repository contains a full-stack **Network Intrusion Detection System (NIDS)** prototype built with:

- `React + Vite` frontend
- `FastAPI` backend
- `SQLite + SQLAlchemy` persistence
- `Python + scikit-learn` machine learning

The project classifies network traffic as `normal` or `malicious`, stores predictions and alerts, and exposes a dashboard for monitoring, analytics, exports, and model evaluation.

## Current Implementation

The working system currently includes:

- JWT login and profile flow
- Live dashboard summary
- Prediction request form (`/predict`)
- Alert creation for malicious predictions
- Alert resolution workflow
- Prediction history with server-side filters
- Analytics timeline with selectable time window
- Hover tooltip on timeline bars
- CSV exports for alerts, predictions, and analytics
- Pagination for alerts and prediction history
- Persisted model evaluation metrics:
  - accuracy
  - precision
  - recall
  - F1-score
  - TP / TN / FP / FN

## Project Structure

- [frontend](D:/ml-project/frontend) React dashboard
- [backend](D:/ml-project/backend) FastAPI API, ML integration, training scripts
- [network_intrusion_detection_research.md](D:/ml-project/network_intrusion_detection_research.md) project research summary
- [nids_full_project_execution_flow.md](D:/ml-project/nids_full_project_execution_flow.md) implementation and execution flow

## Run Locally

### 1. Train the model

```powershell
cd D:\ml-project\backend
python scripts\train_from_csv.py
```

### 2. Start backend

```powershell
cd D:\ml-project\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start frontend

```powershell
cd D:\ml-project\frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 4. Open the app

- Frontend: `http://127.0.0.1:5173`
- Backend docs: `http://127.0.0.1:8000/docs`

Login:

- Email: `admin@nidsdemo.com`
- Password: `admin123`

## Dataset and Model

Current model training uses:

- [nids_dataset.csv](D:/ml-project/backend/data/nids_dataset.csv)
- [train_from_csv.py](D:/ml-project/backend/scripts/train_from_csv.py)

Saved artifact:

- [nids_model.joblib](D:/ml-project/backend/artifacts/nids_model.joblib)

The artifact stores:

- model and attack classifier
- label encoders
- model version
- evaluation metrics

## Main API Areas

- `/auth/login`
- `/auth/profile`
- `/dashboard/summary`
- `/traffic/live`
- `/predict`
- `/predict/history`
- `/alerts`
- `/reports/daily`
- `/reports/analytics`
- `/reports/model-evaluation`
- `/reports/export/alerts`
- `/reports/export/predictions`
- `/reports/export/analytics`

## Current Status

The project is in a strong prototype state for academic demonstration:

- frontend and backend are integrated
- model training and inference are functional
- reporting and exports are implemented
- evaluation metrics are visible in the dashboard

## Recommended Next Steps

- retrain with a larger real dataset
- move secrets and admin defaults to stricter environment configuration
- add deployment configuration for public demo hosting
- update final report screenshots from the running application
