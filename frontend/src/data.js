export const navItems = [
  { id: "overview", label: "Overview" },
  { id: "monitoring", label: "Live Monitoring" },
  { id: "alerts", label: "Alerts" },
  { id: "reports", label: "Reports" },
  { id: "settings", label: "Settings" }
];

export const heroStats = [
  { label: "Packets Scanned", value: "1.28M" },
  { label: "Detected Threats", value: "342" },
  { label: "Critical Alerts", value: "09" }
];

export const metrics = [
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

export const chartValues = [58, 77, 44, 89, 63, 96, 70, 61, 84, 48, 66, 74];

export const feedItems = [
  { ip: "192.168.1.24", attack: "Normal", confidence: "98.2%", time: "13:42:09", state: "safe" },
  { ip: "10.0.0.17", attack: "DDoS", confidence: "94.7%", time: "13:42:05", state: "danger" },
  { ip: "172.16.8.42", attack: "Probe", confidence: "91.1%", time: "13:41:58", state: "warning" },
  { ip: "192.168.0.61", attack: "Normal", confidence: "97.6%", time: "13:41:51", state: "safe" }
];

export const alertRows = [
  { time: "13:41", source: "10.0.0.17", attack: "DDoS", severity: "critical", status: "Open" },
  { time: "13:35", source: "172.16.8.42", attack: "Probe", severity: "high", status: "Investigating" },
  { time: "13:18", source: "192.168.10.4", attack: "Botnet", severity: "critical", status: "Queued" },
  { time: "12:57", source: "192.168.0.19", attack: "Port Scan", severity: "medium", status: "Resolved" }
];

export const modelSummary = [
  { label: "Accuracy", value: "97.4%" },
  { label: "Precision", value: "95.8%" },
  { label: "Recall", value: "96.9%" },
  { label: "F1-Score", value: "96.3%" }
];
