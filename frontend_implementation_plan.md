# Frontend Implementation Plan for NIDS

## Objective

Build a web interface for the Network Intrusion Detection System (NIDS) that allows users to monitor traffic, review alerts, inspect predictions, and manage system activity.

## Recommended Stack

- React.js for frontend development
- HTML5 and CSS3
- JavaScript
- Chart.js or Plotly for data visualization
- Axios or Fetch API for backend communication

## Main Pages

### 1. Login Page

- User login form
- Input validation
- Error message handling
- Session/token storage after login

### 2. Dashboard Page

- Total packets/records processed
- Intrusions detected
- Recent alerts
- Attack distribution chart
- System uptime or service status

### 3. Live Monitoring Page

- Stream of incoming traffic summaries
- Prediction labels: normal or malicious
- Time-wise event table
- Severity indicator

### 4. Alerts Page

- Alert ID
- Attack type
- Timestamp
- Severity
- Status: open/resolved

### 5. Reports Page

- Daily/weekly detection summary
- Exportable logs
- Model performance summary

### 6. Admin or Settings Page

- User management
- Threshold settings
- Model version display
- API health check

## UI Components

- Navbar
- Sidebar
- Summary cards
- Data tables
- Alert badges
- Line/bar/pie charts
- Search and filter controls
- Pagination for logs and alerts

## Frontend Workflow

1. User logs in.
2. Token/session is stored securely.
3. Dashboard fetches summary data from backend APIs.
4. Monitoring page polls or receives periodic updates.
5. Alerts page lists malicious events.
6. Reports page generates filtered summaries.

## API Integration

Frontend should consume:

- `POST /auth/login`
- `GET /dashboard/summary`
- `GET /traffic/live`
- `POST /predict`
- `GET /alerts`
- `GET /reports`
- `GET /health`

## Validation Requirements

- Prevent empty form submission
- Validate date filters
- Handle API timeout and error states
- Show fallback UI when services are unavailable

## Security Requirements for Frontend

- Store tokens securely
- Restrict admin pages by role
- Escape unsafe display content
- Enforce HTTPS in deployment
- Avoid exposing secrets in frontend code

## Deliverables

- Responsive UI screens
- API-connected dashboard
- Live alert visualization
- Reports and filters
- Role-based page access

