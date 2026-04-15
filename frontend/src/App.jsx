import { useEffect, useMemo, useState } from "react";
import {
  fetchAlerts,
  fetchDailyReport,
  fetchDashboardSummary,
  fetchLiveTraffic,
  fetchProfile,
  login,
  runPrediction
} from "./api";
import {
  alertRows,
  chartValues,
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
  const [summary, setSummary] = useState(null);
  const [liveRecords, setLiveRecords] = useState([]);
  const [alerts, setAlerts] = useState(alertRows);
  const [report, setReport] = useState(null);
  const [authForm, setAuthForm] = useState({
    email: "admin@nidsdemo.com",
    password: "admin123"
  });
  const [authLoading, setAuthLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [predictLoading, setPredictLoading] = useState(false);
  const [predictResult, setPredictResult] = useState(null);
  const [error, setError] = useState("");
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

  const filteredAlerts = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return alerts;

    return alerts.filter((row) =>
      Object.values(row).some((value) => String(value).toLowerCase().includes(normalized))
    );
  }, [alerts, query]);

  const chartPoints = useMemo(() => {
    if (!alerts.length) return chartValues;

    const source = alerts
      .slice(0, 12)
      .map((item) => severityToChartValue(item.severity))
      .reverse();

    while (source.length < 12) source.unshift(38);
    return source;
  }, [alerts]);

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

  async function loadBackendData(currentToken) {
    setLoadingData(true);
    setError("");

    try {
      const [profileData, summaryData, liveData, alertsData, reportData] = await Promise.all([
        fetchProfile(currentToken),
        fetchDashboardSummary(currentToken),
        fetchLiveTraffic(currentToken),
        fetchAlerts(currentToken),
        fetchDailyReport(currentToken)
      ]);

      setProfile(profileData);
      setSummary(summaryData);
      setLiveRecords(liveData);
      setAlerts(
        alertsData.map((item) => ({
          time: new Date(item.created_at).toLocaleTimeString(),
          source: item.source_ip,
          attack: item.attack_type,
          severity: item.severity,
          status: item.status
        }))
      );
      setReport(reportData);
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

  useEffect(() => {
    if (!token) return;
    loadBackendData(token);
  }, [token]);

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
              <span className="pill warning">High Activity</span>
            </div>
            <div aria-label="Traffic detection chart" className="chart-bars">
              {chartPoints.map((value, index) => (
                <span key={`${value}-${index}`} style={{ "--value": value }} />
              ))}
            </div>
            <div className="chart-axis">
              <span>00</span>
              <span>04</span>
              <span>08</span>
              <span>12</span>
              <span>16</span>
              <span>20</span>
            </div>
          </article>

          <article className="panel">
            <div className="panel-head">
              <div>
                <p className="eyebrow">Live Feed</p>
                <h3>Recent predictions</h3>
              </div>
              <span className="mono">Updated 5s ago</span>
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
              <button className="ghost-button small" type="button">
                Filter
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
                  </tr>
                </thead>
                <tbody>
                  {filteredAlerts.map((row) => (
                    <tr key={`${row.time}-${row.source}-${row.attack}`}>
                      <td>{row.time}</td>
                      <td>{row.source}</td>
                      <td>{row.attack}</td>
                      <td>
                        <span className={`severity ${row.severity}`}>{capitalize(row.severity)}</span>
                      </td>
                      <td className="status">{row.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
        </section>
      </main>
    </div>
  );
}

function severityToChartValue(severity) {
  if (severity === "critical") return 95;
  if (severity === "high") return 78;
  if (severity === "medium") return 62;
  return 40;
}

function topKey(recordMap) {
  if (!recordMap || typeof recordMap !== "object") return "";

  return Object.entries(recordMap).sort((a, b) => b[1] - a[1])[0]?.[0] || "";
}

function parseError(error) {
  const message = error instanceof Error ? error.message : "Unexpected error";
  if (message.includes("Invalid or expired token")) return "Session expired. Please sign in again.";
  if (message.includes("Failed to fetch")) return "Backend unreachable. Start FastAPI server on port 8000.";
  return message;
}
