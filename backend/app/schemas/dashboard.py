from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_traffic_records: int
    total_predictions: int
    total_alerts: int
    open_alerts: int
    malicious_predictions: int

