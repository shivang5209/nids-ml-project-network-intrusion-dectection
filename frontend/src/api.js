const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function withQuery(path, params = {}) {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "" || value === "all") return;
    search.set(key, String(value));
  });

  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }
  return response.json();
}

async function download(path, token, filename, params = {}) {
  const response = await fetch(`${API_BASE_URL}${withQuery(path, params)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function login(email, password) {
  return request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
}

export async function fetchProfile(token) {
  return request("/auth/profile", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchDashboardSummary(token) {
  return request("/dashboard/summary", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchLiveTraffic(token) {
  return request("/traffic/live", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchAlerts(token, filters = {}) {
  return request(withQuery("/alerts", filters), {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchDailyReport(token) {
  return request("/reports/daily", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchAnalyticsReport(token, hours = 12) {
  return request(`/reports/analytics?hours=${hours}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchPredictionHistory(token, filters = {}) {
  return request(withQuery("/predict/history", filters), {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function runPrediction(token, payload) {
  return request("/predict", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

export async function updateAlertStatus(token, alertId, status) {
  return request(`/alerts/${alertId}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ status })
  });
}

export async function downloadAlertsReport(token, filters = {}) {
  return download("/reports/export/alerts", token, "nids-alerts-report.csv", filters);
}

export async function downloadPredictionsReport(token, filters = {}) {
  return download("/reports/export/predictions", token, "nids-predictions-report.csv", filters);
}

export async function downloadAnalyticsReport(token, hours = 12) {
  return download(`/reports/export/analytics?hours=${hours}`, token, `nids-analytics-${hours}h.csv`);
}
