import { useEffect, useMemo, useState } from "react";
import {
  downloadAlertsReport,
  downloadAnalyticsReport,
  downloadPredictionsReport,
  fetchAlerts,
  fetchAnalyticsReport,
  fetchDailyReport,
  fetchDashboardSummary,
  fetchLiveTraffic,
  fetchPredictionHistory,
  fetchProfile,
  login,
  runPrediction,
  updateAlertStatus
} from "./api";
import {
  alertRows,
  feedItems,
  navItems
} from "./data";

const panelTitles = {
  overview: "Overview",
  monitoring: "Live Monitoring",
  alerts: "Alerts",
  reports: "Reports",
  settings: "Settings"
};

function severityClass(value) {
  if (value === "danger") return "critical";
  if (value === "warning") return "high";
  return "medium";
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("nids_token") || "");
  const [profile, setProfile] = useState(null);
  const [activePanel, setActivePanel] = useState("overview");
  const [query, setQuery] = useState("");
  const [alertSeverityFilter, setAlertSeverityFilter] = useState("all");
  const [alertStatusFilter, setAlertStatusFilter] = useState("all");
  const [historyLabelFilter, setHistoryLabelFilter] = useState("all");
  const [analyticsWindow, setAnalyticsWindow] = useState("12");
  const [alertsPage, setAlertsPage] = useState(1);
  const [historyPage, setHistoryPage] = useState(1);
  const [summary, setSummary] = useState(null);
  const [liveRecords, setLiveRecords] = useState([]);
  const [alerts, setAlerts] = useState(alertRows);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [alertsMeta, setAlertsMeta] = useState({ total: 0, page: 1, page_size: 10 });
  const [historyMeta, setHistoryMeta] = useState({ total: 0, page: 1, page_size: 10 });
  const [report, setReport] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [authForm, setAuthForm] = useState({
    email: "admin@nidsdemo.com",
    password: "admin123"
  });
  const [authLoading, setAuthLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [predictLoading, setPredictLoading] = useState(false);
  const [alertUpdatingId, setAlertUpdatingId] = useState(null);
  const [predictResult, setPredictResult] = useState(null);
  const [error, setError] = useState("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const [predictForm, setPredictForm] = useState({
    source_ip: "10.0.0.17",
    destination_ip: "192.168.1.25",
    protocol: "TCP",
    packet_count: 650,
    byte_count: 250000,
    flow_duration: 0.42
  });

  const modelSummary = useMemo(() => {
    if (!report) {
      return [
        { label: "Accuracy", value: "97.4%" },
        { label: "Precision", value: "95.8%" },
        { label: "Recall", value: "96.9%" },
        { label: "F1-Score", value: "96.3%" }
      ];
    }

    return [
      { label: "Predictions", value: String(report.prediction_count || 0) },
      { label: "Alerts", value: String(report.alert_count || 0) },
      { label: "Top Label", value: topKey(report.labels) || "N/A" },
      { label: "Top Attack", value: topKey(report.attack_types) || "N/A" }
    ];
  }, [report]);

  const heroStats = useMemo(() => {
    if (!summary) {
      return [
        { label: "Packets Scanned", value: "1.28M" },
        { label: "Detected Threats", value: "342" },
        { label: "Critical Alerts", value: "09" }
      ];
    }

    return [
      { label: "Packets Scanned", value: String(summary.total_traffic_records) },
      { label: "Detected Threats", value: String(summary.malicious_predictions) },
      { label: "Critical Alerts", value: String(summary.open_alerts) }
    ];
  }, [summary]);

  const metrics = useMemo(() => {
    if (!summary || !report) {
      return [
        {
          label: "Traffic Health",
          value: "87%",
          description: "Normal traffic share over the last 24 hours."
        },
        {
          label: "False Positive Rate",
          value: "2.8%",
          description: "Current operational rate after threshold tuning."
        },
        {
          label: "Top Attack",
          value: "DDoS",
          description: "Most frequent detected category in current stream."
        },
        {
          label: "Active Analysts",
          value: "04",
          description: "Users reviewing incident traffic and alert queue."
        }
      ];
    }

    const totalPredictions = summary.total_predictions || 1;
    const normalRate = Math.max(
      0,
      ((totalPredictions - summary.malicious_predictions) / totalPredictions) * 100
    );

    return [
      {
        label: "Traffic Health",
        value: `${normalRate.toFixed(1)}%`,
        description: "Estimated normal traffic share from backend summaries."
      },
      {
        label: "Open Alerts",
        value: String(summary.open_alerts),
        description: "Current unresolved incidents requiring analyst review."
      },
      {
        label: "Top Attack",
        value: topKey(report.attack_types) || "N/A",
        description: "Most frequent attack label from report aggregation."
      },
      {
        label: "Logged User",
        value: profile?.name || "Unknown",
        description: "Authenticated operator for this dashboard session."
      }
    ];
  }, [profile?.name, report, summary]);

  const filteredAlerts = alerts;

  const filteredHistory = predictionHistory;

  const chartPoints = useMemo(() => {
    if (!analytics?.timeline?.length) {
      return Array.from({ length: 12 }, (_, index) => ({
        label: `${String(index * 2).padStart(2, "0")}:00`,
        count: 0,
        malicious_count: 0,
        chartValue: 18
      }));
    }

    const source = analytics.timeline.map((item) => ({
      ...item,
      chartValue: countToChartValue(item.count)
    }));

    return source.every((item) => item.chartValue === 18)
      ? source.map((item) => ({ ...item, chartValue: 26 }))
      : source;
  }, [analytics]);

  const chartAxisLabels = useMemo(() => {
    if (!analytics?.timeline?.length) {
      return ["00", "04", "08", "12", "16", "20"];
    }

    return analytics.timeline
      .filter((_, index) => {
        const interval = analytics.timeline.length > 24 ? 6 : analytics.timeline.length > 12 ? 4 : 2;
        return index % interval === 0;
      })
      .map((item) => item.label.slice(0, 2));
  }, [analytics]);

  const attackHighlights = useMemo(() => {
    const entries = Object.entries(analytics?.attack_distribution || {});
    if (!entries.length) {
      return [
        { label: "Normal Window", value: "No attacks detected" },
        { label: "Timeline", value: "Awaiting predictions" },
      ];
    }

    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([label, value]) => ({ label, value: `${value} events` }));
  }, [analytics]);

  const displayFeed = useMemo(() => {
    if (!liveRecords.length) return feedItems;

    return liveRecords.slice(0, 6).map((item) => {
      const state =
        item.packet_count > 1400 || item.byte_count > 800000
          ? "danger"
          : item.packet_count > 500
            ? "warning"
            : "safe";

      return {
        ip: `${item.source_ip} -> ${item.destination_ip}`,
        attack: item.protocol,
        confidence: state === "danger" ? "High Risk" : state === "warning" ? "Monitor" : "Normal",
        time: new Date(item.captured_at).toLocaleTimeString(),
        state
      };
    });
  }, [liveRecords]);

  const baseFilters = useMemo(() => ({ q: query }), [query]);
  const alertFilters = useMemo(() => ({
    ...baseFilters,
    severity: alertSeverityFilter,
    status: alertStatusFilter,
    page: alertsPage,
    page_size: 10
  }), [alertSeverityFilter, alertStatusFilter, alertsPage, baseFilters]);
  const historyFilters = useMemo(() => ({
    ...baseFilters,
    label: historyLabelFilter,
    page: historyPage,
    page_size: 10
  }), [baseFilters, historyLabelFilter, historyPage]);

  async function loadBackendData(currentToken, selectedWindow = analyticsWindow) {
    setLoadingData(true);
    setError("");

    try {
      const [profileData, summaryData, liveData, alertsData, reportData, historyData, analyticsData] = await Promise.all([
        fetchProfile(currentToken),
        fetchDashboardSummary(currentToken),
        fetchLiveTraffic(currentToken),
        fetchAlerts(currentToken, alertFilters),
        fetchDailyReport(currentToken),
        fetchPredictionHistory(currentToken, historyFilters),
        fetchAnalyticsReport(currentToken, Number(selectedWindow))
      ]);

      setProfile(profileData);
      setSummary(summaryData);
      setLiveRecords(liveData);
      setAlerts(
        alertsData.items.map((item) => ({
          id: item.id,
          time: new Date(item.created_at).toLocaleTimeString(),
          source: item.source_ip,
          attack: item.attack_type,
          severity: item.severity,
          status: item.status
        }))
      );
      setAlertsMeta({
        total: alertsData.total,
        page: alertsData.page,
        page_size: alertsData.page_size
      });
      setReport(reportData);
      setPredictionHistory(historyData.items);
      setHistoryMeta({
        total: historyData.total,
        page: historyData.page,
        page_size: historyData.page_size
      });
      setAnalytics(analyticsData);
      setLastUpdatedAt(new Date());
    } catch (err) {
      setError(parseError(err));
      clearSession();
    } finally {
      setLoadingData(false);
    }
  }

  function clearSession() {
    setToken("");
    setProfile(null);
    localStorage.removeItem("nids_token");
  }

  async function handleLogin(event) {
    event.preventDefault();
    setAuthLoading(true);
    setError("");

    try {
      const payload = await login(authForm.email, authForm.password);
      setToken(payload.access_token);
      localStorage.setItem("nids_token", payload.access_token);
    } catch (err) {
      setError(parseError(err));
    } finally {
      setAuthLoading(false);
    }
  }

  async function handlePredict(event) {
    event.preventDefault();
    if (!token) return;

    setPredictLoading(true);
    setError("");

    try {
      const payload = {
        ...predictForm,
        packet_count: Number(predictForm.packet_count),
        byte_count: Number(predictForm.byte_count),
        flow_duration: Number(predictForm.flow_duration)
      };
      const result = await runPrediction(token, payload);
      setPredictResult(result);
      await loadBackendData(token);
    } catch (err) {
      setError(parseError(err));
    } finally {
      setPredictLoading(false);
    }
  }

  async function handleResolveAlert(alertId) {
    if (!token || !alertId) return;

    setAlertUpdatingId(alertId);
    setError("");

    try {
      await updateAlertStatus(token, alertId, "Resolved");
      await loadBackendData(token);
    } catch (err) {
      setError(parseError(err));
    } finally {
      setAlertUpdatingId(null);
    }
  }

  function downloadCsv(filename, rows) {
    if (!rows.length) return;

    const columns = Object.keys(rows[0]);
    const csvContent = [
      columns.join(","),
      ...rows.map((row) =>
        columns
          .map((column) => `"${String(row[column] ?? "").replaceAll('"', '""')}"`)
          .join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function exportAlerts() {
    if (!token) return;

    try {
      await downloadAlertsReport(token, alertFilters);
    } catch (err) {
      setError(parseError(err));
    }
  }

  async function exportHistory() {
    if (!token) return;

    try {
      await downloadPredictionsReport(token, historyFilters);
    } catch (err) {
      setError(parseError(err));
    }
  }

  async function exportAnalytics() {
    if (!token) return;

    try {
      await downloadAnalyticsReport(token, Number(analyticsWindow));
    } catch (err) {
      setError(parseError(err));
    }
  }

  useEffect(() => {
    if (!token) return;
    loadBackendData(token);
  }, [
    alertSeverityFilter,
    alertStatusFilter,
    analyticsWindow,
    alertsPage,
    historyLabelFilter,
    historyPage,
    query,
    token
  ]);

  useEffect(() => {
    if (!token) return undefined;

    const intervalId = window.setInterval(() => {
      loadBackendData(token);
    }, 15000);

    return () => window.clearInterval(intervalId);
  }, [
    alertSeverityFilter,
    alertStatusFilter,
    analyticsWindow,
    alertsPage,
    historyLabelFilter,
    historyPage,
    query,
    token
  ]);

  useEffect(() => {
    setAlertsPage(1);
  }, [alertSeverityFilter, alertStatusFilter, query]);

  useEffect(() => {
    setHistoryPage(1);
  }, [historyLabelFilter, query]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">N</div>
          <div>
            <p className="eyebrow">Security Console</p>
            <h1>NIDS Control</h1>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item${activePanel === item.id ? " active" : ""}`}
              onClick={() => setActivePanel(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <section className="status-card">
          <p className="eyebrow">Model State</p>
          <h2>{profile ? "Backend Connected" : "Offline Mode"}</h2>
          <p className="muted">
            {profile
              ? `Signed in as ${profile.name} (${profile.role})`
              : "Sign in to load live traffic, alerts, and report data."}
          </p>
          <div className="status-row">
            <span className={`pill ${profile ? "online" : "warning"}`}>
              {profile ? "Online" : "Disconnected"}
            </span>
            {profile ? (
              <button className="ghost-button small" onClick={clearSession} type="button">
                Logout
              </button>
            ) : null}
          </div>
        </section>
      </aside>

      <main className="main">
        {!token ? (
          <section className="auth-panel">
            <p className="eyebrow">Backend Authentication</p>
            <h2>Connect Dashboard</h2>
            <p className="muted">
              Use seeded admin credentials to load live API data from FastAPI.
            </p>
            <form className="auth-form" onSubmit={handleLogin}>
              <label>
                Email
                <input
                  onChange={(event) =>
                    setAuthForm((prev) => ({ ...prev, email: event.target.value }))
                  }
                  type="email"
                  value={authForm.email}
                />
              </label>
              <label>
                Password
                <input
                  onChange={(event) =>
                    setAuthForm((prev) => ({ ...prev, password: event.target.value }))
                  }
                  type="password"
                  value={authForm.password}
                />
              </label>
              <button className="ghost-button auth-submit" disabled={authLoading} type="submit">
                {authLoading ? "Signing In..." : "Sign In"}
              </button>
            </form>
          </section>
        ) : null}

        {error ? <p className="error-banner">{error}</p> : null}

        <header className="topbar">
          <div>
            <p className="eyebrow">Network Intrusion Detection System</p>
            <h2>{panelTitles[activePanel]}</h2>
          </div>
          <div className="topbar-actions">
            <div className="search-wrap">
              <input
                aria-label="Search alerts, IPs, attacks"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search alerts, IPs, attacks"
                type="search"
                value={query}
              />
            </div>
            <button
              className="ghost-button"
              disabled={!token || loadingData}
              onClick={() => loadBackendData(token)}
              type="button"
            >
              {loadingData ? "Refreshing..." : "Refresh Data"}
            </button>
          </div>
        </header>

        <section className="filters-row">
          <label>
            Alert Severity
            <select
              onChange={(event) => setAlertSeverityFilter(event.target.value)}
              value={alertSeverityFilter}
            >
              <option value="all">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
            </select>
          </label>
          <label>
            Alert Status
            <select
              onChange={(event) => setAlertStatusFilter(event.target.value)}
              value={alertStatusFilter}
            >
              <option value="all">All</option>
              <option value="open">Open</option>
              <option value="queued">Queued</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
            </select>
          </label>
          <label>
            History Label
            <select
              onChange={(event) => setHistoryLabelFilter(event.target.value)}
              value={historyLabelFilter}
            >
              <option value="all">All</option>
              <option value="normal">Normal</option>
              <option value="malicious">Malicious</option>
            </select>
          </label>
          <label>
            Analytics Window
            <select
              onChange={(event) => setAnalyticsWindow(event.target.value)}
              value={analyticsWindow}
            >
              <option value="12">Last 12 Hours</option>
              <option value="24">Last 24 Hours</option>
              <option value="48">Last 48 Hours</option>
              <option value="72">Last 72 Hours</option>
            </select>
          </label>
        </section>

        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Active Watch</p>
            <h3>Traffic risk is elevated on the campus gateway.</h3>
            <p className="muted">
              The system is monitoring inbound and outbound traffic, classifying attack patterns,
              and surfacing alerts for analyst review.
            </p>
          </div>
          <div className="hero-grid">
            {heroStats.map((item) => (
              <div className="hero-stat" key={item.label}>
                <span className="eyebrow">{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="metrics">
          {metrics.map((item) => (
            <article className="metric-card" key={item.label}>
              <p className="eyebrow">{item.label}</p>
              <h3>{item.value}</h3>
              <p className="muted">{item.description}</p>
            </article>
          ))}
        </section>

        <section className="content-grid">
          <article className="panel tall">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Traffic Timeline</p>
                <h3>Detection intensity</h3>
              </div>
              <span className="pill warning">
                {analytics
                  ? `${analytics.malicious_prediction_count || 0} flagged in ${analytics.window_hours}h`
                  : "High Activity"}
              </span>
            </div>
            <div className="panel-actions chart-actions">
              <button className="ghost-button small" onClick={exportAnalytics} type="button">
                Export Analytics CSV
              </button>
            </div>
            <div className="chart-stage">
              <div aria-label="Traffic detection chart" className="chart-bars">
                {chartPoints.map((item) => (
                  <div className="chart-bar-wrap" key={item.hour || item.label}>
                    <button
                      aria-label={`${item.label} with ${item.count} predictions`}
                      className="chart-bar-button"
                      style={{ "--value": item.chartValue }}
                      title={`${item.label} | Predictions: ${item.count} | Malicious: ${item.malicious_count}`}
                      type="button"
                    />
                    <div className="chart-tooltip" role="status">
                      <span className="eyebrow">Time Slot</span>
                      <strong>{item.label}</strong>
                      <p>Predictions: {item.count}</p>
                      <p>Malicious: {item.malicious_count}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="chart-axis">
              {chartAxisLabels.map((label) => (
                <span key={label}>{label}</span>
              ))}
            </div>
            <div className="chart-highlights">
              {attackHighlights.map((item) => (
                <article className="chart-highlight" key={item.label}>
                  <span className="eyebrow">{item.label}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Live Feed</p>
                <h3>Recent predictions</h3>
              </div>
              <span className="mono">
                {lastUpdatedAt
                  ? `Updated ${lastUpdatedAt.toLocaleTimeString()}`
                  : "Waiting for backend"}
              </span>
            </div>
            <div className="feed-list">
              {displayFeed.map((item) => (
                <article className="feed-item" key={`${item.ip}-${item.time}`}>
                  <div className="feed-item-head">
                    <strong>{item.ip}</strong>
                    <span className={`severity ${severityClass(item.state)}`}>{item.attack}</span>
                  </div>
                  <div className="feed-item-meta">
                    <span className="mono">Confidence {item.confidence}</span>
                    <span className="mono">{item.time}</span>
                  </div>
                </article>
              ))}
            </div>
          </article>

          <article className="panel wide">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Inference Lab</p>
                <h3>Run prediction request</h3>
              </div>
              <span className="mono">POST /predict</span>
            </div>
            <form className="predict-form" onSubmit={handlePredict}>
              <label>
                Source IP
                <input
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, source_ip: event.target.value }))
                  }
                  required
                  type="text"
                  value={predictForm.source_ip}
                />
              </label>
              <label>
                Destination IP
                <input
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, destination_ip: event.target.value }))
                  }
                  required
                  type="text"
                  value={predictForm.destination_ip}
                />
              </label>
              <label>
                Protocol
                <select
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, protocol: event.target.value }))
                  }
                  value={predictForm.protocol}
                >
                  <option value="TCP">TCP</option>
                  <option value="UDP">UDP</option>
                  <option value="ICMP">ICMP</option>
                </select>
              </label>
              <label>
                Packet Count
                <input
                  min="0"
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, packet_count: event.target.value }))
                  }
                  required
                  type="number"
                  value={predictForm.packet_count}
                />
              </label>
              <label>
                Byte Count
                <input
                  min="0"
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, byte_count: event.target.value }))
                  }
                  required
                  type="number"
                  value={predictForm.byte_count}
                />
              </label>
              <label>
                Flow Duration
                <input
                  min="0"
                  onChange={(event) =>
                    setPredictForm((prev) => ({ ...prev, flow_duration: event.target.value }))
                  }
                  required
                  step="0.01"
                  type="number"
                  value={predictForm.flow_duration}
                />
              </label>
              <button
                className="ghost-button predict-submit"
                disabled={!token || predictLoading}
                type="submit"
              >
                {predictLoading ? "Running..." : "Run Prediction"}
              </button>
            </form>

            {predictResult ? (
              <div className="predict-result">
                <span className="eyebrow">Latest Result</span>
                <p>
                  Label: <strong>{predictResult.label}</strong> | Attack:{" "}
                  <strong>{predictResult.attack_type}</strong> | Confidence:{" "}
                  <strong>{(predictResult.confidence * 100).toFixed(1)}%</strong>
                </p>
                <p className="muted">
                  Prediction ID: {predictResult.prediction_id} | Alert Created:{" "}
                  {predictResult.alert_created ? "Yes" : "No"}
                </p>
              </div>
            ) : null}
          </article>

          <article className="panel wide">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Alert Queue</p>
                <h3>Incident review</h3>
              </div>
              <button className="ghost-button small" onClick={exportAlerts} type="button">
                Export CSV
              </button>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Source</th>
                    <th>Attack</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAlerts.map((row) => (
                    <tr key={row.id ?? `${row.time}-${row.source}-${row.attack}`}>
                      <td>{row.time}</td>
                      <td>{row.source}</td>
                      <td>{row.attack}</td>
                      <td>
                        <span className={`severity ${row.severity}`}>{capitalize(row.severity)}</span>
                      </td>
                      <td className="status">{row.status}</td>
                      <td>
                        <button
                          className="ghost-button small"
                          disabled={row.status === "Resolved" || alertUpdatingId === row.id}
                          onClick={() => handleResolveAlert(row.id)}
                          type="button"
                        >
                          {alertUpdatingId === row.id ? "Saving..." : "Resolve"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-pagination">
              <span className="mono">
                Page {alertsMeta.page} of {Math.max(1, Math.ceil(alertsMeta.total / alertsMeta.page_size))}
              </span>
              <div className="panel-actions">
                <button
                  className="ghost-button small"
                  disabled={alertsMeta.page <= 1}
                  onClick={() => setAlertsPage((current) => Math.max(1, current - 1))}
                  type="button"
                >
                  Previous
                </button>
                <button
                  className="ghost-button small"
                  disabled={alertsMeta.page >= Math.ceil(alertsMeta.total / alertsMeta.page_size)}
                  onClick={() => setAlertsPage((current) => current + 1)}
                  type="button"
                >
                  Next
                </button>
              </div>
            </div>
          </article>

          <article className="panel">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Model Summary</p>
                <h3>Performance snapshot</h3>
              </div>
            </div>
            <ul className="report-list">
              {modelSummary.map((item) => (
                <li key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </li>
              ))}
            </ul>
          </article>

          <article className="panel wide">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Prediction History</p>
                <h3>Recent inference decisions</h3>
              </div>
              <div className="panel-actions">
                <span className="mono">GET /predict/history</span>
                <button className="ghost-button small" onClick={exportHistory} type="button">
                  Export CSV
                </button>
              </div>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Label</th>
                    <th>Attack</th>
                    <th>Confidence</th>
                    <th>Model</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.slice(0, 10).map((row) => (
                    <tr key={row.id}>
                      <td>{new Date(row.predicted_at).toLocaleTimeString()}</td>
                      <td>{row.predicted_label}</td>
                      <td>{row.attack_type}</td>
                      <td>{(row.confidence_score * 100).toFixed(1)}%</td>
                      <td className="status">{row.model_version}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-pagination">
              <span className="mono">
                Page {historyMeta.page} of {Math.max(1, Math.ceil(historyMeta.total / historyMeta.page_size))}
              </span>
              <div className="panel-actions">
                <button
                  className="ghost-button small"
                  disabled={historyMeta.page <= 1}
                  onClick={() => setHistoryPage((current) => Math.max(1, current - 1))}
                  type="button"
                >
                  Previous
                </button>
                <button
                  className="ghost-button small"
                  disabled={historyMeta.page >= Math.ceil(historyMeta.total / historyMeta.page_size)}
                  onClick={() => setHistoryPage((current) => current + 1)}
                  type="button"
                >
                  Next
                </button>
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}

function topKey(recordMap) {
  if (!recordMap || typeof recordMap !== "object") return "";

  return Object.entries(recordMap).sort((a, b) => b[1] - a[1])[0]?.[0] || "";
}

function countToChartValue(count) {
  const normalized = Math.min(count, 12);
  return 18 + normalized * 6;
}

function parseError(error) {
  const message = error instanceof Error ? error.message : "Unexpected error";
  if (message.includes("Invalid or expired token")) return "Session expired. Please sign in again.";
  if (message.includes("Failed to fetch")) return "Backend unreachable. Start FastAPI server on port 8000.";
  return message;
}
