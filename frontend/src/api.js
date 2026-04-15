const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }
  return response.json();
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

export async function fetchAlerts(token) {
  return request("/alerts", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function fetchDailyReport(token) {
  return request("/reports/daily", {
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
