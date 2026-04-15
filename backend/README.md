# NIDS Backend

FastAPI backend for the Network Intrusion Detection System project.

## Features

- JWT login and profile endpoints
- Traffic ingestion and live feed endpoints
- Baseline prediction endpoint with alert generation
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

## Default Admin

- Email: `admin@nidsdemo.com`
- Password: `admin123`

Change these in `.env` before production/demo use.
