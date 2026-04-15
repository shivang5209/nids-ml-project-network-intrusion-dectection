# Machine Learning Network Intrusion Detection Systems: Working Principles and Implementation Guide

## Executive summary

This report investigates the most common and practically useful interpretations of the user’s unspecified “system/topic,” then selects and deeply analyzes the one most consistent with the provided context: a **Machine Learning–based Network Intrusion Detection System (ML-NIDS)** that classifies network activity as **benign vs. malicious** and supports **near-real-time monitoring via a web interface**. This aligns with the uploaded research brief describing an ML-based NIDS pipeline (collection → preprocessing → feature engineering → model training → real-time inference → dashboard/alerts) and explicit system requirements and deployment goals. fileciteturn0file0

Key conclusions supported by primary sources and reputable research:

A production-grade ML-NIDS is rarely “ML-only.” The most robust path is a **hybrid** of (a) well-established **signature/rule IDS/IPS engines** (e.g., Suricata/Snort) and (b) **ML anomaly/behavior models** fed by flow/protocol metadata (e.g., CICFlowMeter-like features, Zeek logs). NIST’s IDS/IPS guideline explicitly emphasizes the breadth of IDPS technologies and deployment modes, making hybrid designs a mainstream best practice for balancing coverage and operational feasibility. citeturn0search8turn0search12turn35search1turn35search2

In practice, the core engineering challenge is not “choosing a classifier,” but building an **end-to-end telemetry and decision pipeline** with predictable latency, low false-alarm rates, robust updates, and safe operations under drift and adversarial pressure. Modern research highlights the need to address **concept drift** (traffic patterns change), **encrypted traffic visibility limits**, and **evasion/adversarial ML** concerns. citeturn8search2turn9search3turn9search14turn28view0

Real-world and empirical outcomes show what’s achievable under controlled settings:  
- **Kitsune/KitNET** demonstrates strong anomaly-detection performance (AUC/EER reported across attack datasets) and provides **edge-feasible throughput** on constrained hardware; the paper reports roughly **~1,000 packets/s** on a Raspberry Pi with a single autoencoder and **~5,400 packets/s** with an ensemble (k=35); on a stronger PC baseline it reports **~7,500 packets/s** and **~37,300 packets/s** respectively. citeturn28view0turn27view1  
- **N-BaIoT** reports enterprise-relevant botnet detection characteristics: **TPR 100%**, mean **FPR 0.007±0.01**, and **174±212 ms** mean detection time in their test setup, illustrating the operational value of low-latency anomaly detection for IoT botnet activity. citeturn34view0turn33view0

Finally, this report provides a step-by-step implementation plan and checklists, option-comparison tables (tools, architectures, storage/search backends), and effort/cost estimates under explicit assumptions.

## Definition and scope of the topic

Because the user did not specify the topic, the “system” can plausibly refer to several related—but materially different—security systems:

A likely interpretation is an **ML-based Network Intrusion Detection System (ML-NIDS)** that monitors network traffic, extracts features (packets/flows/protocol logs), and runs ML models to classify or score suspicious behavior—matching the uploaded brief’s objective, methodology, and deployment intent (web dashboard + live monitoring). fileciteturn0file0

Two other common interpretations are:  
A **general Intrusion Detection and Prevention System (IDPS)**—including signature-based detection, anomaly detection, and IPS blocking—and an **HIDS/XDR-style endpoint IDS** where host logs and endpoint telemetry drive ML detection rather than packet/flow data. NIST’s guide frames IDPS broadly and distinguishes multiple types (including network-based and host-based), making this ambiguity reasonable. citeturn0search8turn0search12turn8search1

This report selects **ML-NIDS** as the primary focus because it is the most actionable and most aligned with the attached project description (live packet monitoring, ML training, web interface, reduced false alarms). fileciteturn0file0

Within ML-NIDS, the scope splits into three operational levels:

Packet-centric NIDS uses DPI-like packet parsing and payload inspection when available. Flow-centric NIDS uses aggregated “biflow” statistics (often feasible even when payload is encrypted). Protocol-metadata NIDS uses structured logs from network analyzers such as Zeek’s connection logs and protocol logs. Zeek documentation demonstrates the common workflow of producing JSON logs from either live interfaces or stored traffic for analysis pipelines. citeturn35search2turn3search11

## How an ML-based NIDS works

An ML-NIDS is best understood as two coupled loops: a **real-time decision loop** and a **model lifecycle loop**.

### Real-time decision loop

At runtime, the ML-NIDS must (a) observe traffic, (b) represent it compactly, (c) score/classify it, then (d) route decisions to alerting/response systems.

Common observation modes are:

Full packet capture (PCAP) for deep forensics and replay; but expensive at scale. Flow export using standards like IPFIX (IETF) or NetFlow v9, which formalize flow-record export to collectors. citeturn7search2turn7search3  
Network threat-detection engines such as Suricata, which can output alerts and rich protocol metadata via **EVE JSON**, described as a “firehose” of alerts/anomalies/metadata into JSON records. citeturn35search1  
Network analysis frameworks like Zeek, which output structured logs (e.g., conn.log) and can represent flows/transactions without relying on payload inspection. citeturn35search2turn3search1

Feature representation usually follows one of two approaches:

Flow-feature extraction: tools like CICFlowMeter generate bidirectional flows (biflows) and extract statistical features; CICFlowMeter documentation describes biflow generation from PCAP and flow-direction semantics (first packet defines forward direction). citeturn7search1turn7search5turn38search6  
Incremental statistics from packet streams: Kitsune/AfterImage-style feature extraction maintains incremental statistics over many “channels,” enabling online anomaly modeling without storing all packets. citeturn25view0turn28view0

Once features exist, models typically fall into:

Supervised classifiers (e.g., Random Forest, SVM, Gradient Boosting), which often perform strongly on labeled benchmarks but require ongoing labeling discipline (as highlighted in the project brief). fileciteturn0file0  
Unsupervised/semi-supervised anomaly detectors (e.g., autoencoders, isolation forests) which can be trained primarily on “normal” traffic. Kitsune’s core idea is an **ensemble of autoencoders (KitNET)** for online unsupervised anomaly detection. citeturn24search0turn28view0  
Hybrid designs where rule/signature alerts become features for ML, or ML produces “suspicion scores” that are then filtered or confirmed by signatures.

### Model lifecycle loop

A production ML-NIDS needs repeatable model governance: dataset versioning, evaluation, staged rollout, and continuous monitoring for drift and regressions.

Two forces dominate:

Concept drift: traffic distribution changes over time; drift-aware IDS research proposes online learning designs to adapt to non-stationary data. citeturn9search3turn9search11  
Limited visibility under encryption: modern networks have pervasive TLS/QUIC; surveys of ML-driven encrypted traffic analysis emphasize that feature extraction shifts toward metadata patterns and timing/size/sequence features. citeturn9search2turn9search6turn9search14

NIST’s AI Risk Management Framework (AI RMF) is useful here as a governance scaffold for AI systems, emphasizing ongoing risk management and lifecycle controls (relevant to drift, monitoring, and operational safety). citeturn8search2turn8search14

### Reference architecture flowchart

```mermaid
flowchart TB
  A[Traffic Sources\n(DC, Campus, Cloud VPC/VNet,\nIoT, Branch)] --> B[Collection Layer\nTAP/SPAN, VPC mirroring,\nPCAP, IPFIX/NetFlow]
  B --> C1[Signature/Protocol Sensors\nSuricata/Snort]
  B --> C2[Network Telemetry\nZeek logs / flow logs]
  C1 --> D[Event Stream\nEVE JSON / Alerts]
  C2 --> E[Feature Stream\nFlow+Protocol metadata]
  D --> F[Streaming Bus\nKafka/Redpanda/Pulsar]
  E --> F
  F --> G[Feature Engineering\nNormalization, windows,\nentity keys]
  G --> H[Online Inference Service\nREST/gRPC\nthresholding + rules]
  H --> I[Alerting & Case Mgmt\nSIEM/SOAR, ticketing]
  H --> J[Storage\nOpenSearch/ClickHouse/S3]
  J --> K[Dashboard\nKibana/OpenSearch Dashboards\nGrafana/custom web]
  J --> L[Model Monitoring\nDrift, latency,\nfalse positives]
  L --> M[Retraining Pipeline\nlabeling + evaluation + CI/CD]
  M --> H
```

## Implementation blueprint and best practices

This section translates the above mechanics into an implementable system design, emphasizing interfaces, data flows, security, scalability, testing, and deployment.

### Implementation steps

Start by choosing a telemetry strategy, because it determines everything downstream.

Traffic acquisition: in enterprise networks this commonly uses SPAN/TAP or virtual packet mirroring. Managed services in cloud environments use provider-specific mirroring and inspection architectures; for example, Google Cloud IDS describes a Google-managed peered network where mirrored traffic is inspected by threat protection technologies, reflecting a “mirror → inspect → alert” pattern regardless of vendor implementation. citeturn39search0

Sensor and log format selection: Suricata’s EVE JSON output is a common integration point because it exports alerts and metadata as JSON records in a single stream/file (“firehose”). citeturn35search1 Zeek similarly produces structured logs (often used in JSON), with conn.log being a foundational connection record for building higher-level features. citeturn35search2

Feature extraction: if you plan ML over flow features, standardize on a feature spec and extraction line. The CIC community datasets explicitly use CICFlowMeter-V3 and extract “more than 80 traffic features,” indicating how common flow-feature sets are in IDS benchmarking. citeturn7search9turn6search2

Model development: the uploaded brief’s baseline model shortlist (Logistic Regression, Decision Trees/Random Forest, SVM, Gradient Boosting) is a reasonable start for interpretable, maintainable baselines. fileciteturn0file0 For anomaly detection, consider autoencoders (Kitsune, N-BaIoT) when labeled data is scarce or the threat space changes rapidly. citeturn28view0turn34view0

Model serving: use an inference service with explicit SLOs (latency, throughput), consistent serialization (e.g., ONNX for portability), and versioned model artifacts. If you choose Python for MVP, FastAPI is a mainstream API framework; PyPI lists FastAPI 0.135.3 (released Apr 1, 2026) and its GitHub LICENSE confirms MIT licensing. citeturn13view3turn14view0

User interface and operations: the uploaded brief calls for a web dashboard for monitoring and response. fileciteturn0file0 In practice, teams often combine a SOC UI (OpenSearch Dashboards/Kibana/Grafana) with workflow systems (case mgmt / ticketing).

### Security and governance best practices

Treat the NIDS pipeline as security-critical infrastructure:

Hardening and continuous monitoring: NIST SP 800-137 provides guidance on building continuous monitoring strategy for assets, threats, and control effectiveness—relevant for operating NIDS pipelines and their telemetry/logging dependencies. citeturn8search1turn8search13  
Data governance: even if payload is not stored, network telemetry can include sensitive identifiers (IPs, hostnames, URLs, SNI, user agents). Implement minimization, access controls, encryption at rest/in transit, and retention policies. citeturn8search2turn39search2  
Adversarial considerations: Kitsune explicitly discusses adversarial attack considerations and the risk of assuming all traffic is benign during training mode, reinforcing the need for safe bootstrapping and contamination checks. citeturn28view0

### Scalability and performance best practices

Performance bottlenecks usually occur in: packet capture, pattern matching, JSON log volumes, and storage/query.

Suricata optimization: Suricata documentation covers performance tuning features like Hyperscan configuration. citeturn35search0 Intel’s benchmarking brief reports Hyperscan can enable Suricata to run “up to four times faster” and shows throughput improvements (e.g., 80→330 Mbps on 1 core/1 thread; 163→637 Mbps on 2 cores/2 threads in their test configuration), plus substantial memory footprint reduction (80 MB → 8 MB for the pattern database in the illustrated example). citeturn37view0turn37view1

Streaming and indexing: event streaming platforms like Apache Kafka are commonly used for high-throughput ingestion; Apache Kafka’s release announcements show Kafka 4.1.2 released March 17, 2026. citeturn15search0 Kafka’s LICENSE in Apache’s repository confirms Apache License 2.0. citeturn17search0

Analytics storage: OpenSearch is a common open-source choice for search + log analytics; OpenSearch releases show version 3.6.0 as “Latest” in early April 2026. citeturn15search5 Its license file indicates Apache 2.0. citeturn16search1 Elastic’s FAQ explains Elasticsearch/Kibana moved from Apache 2.0-licensed source to dual licensing (SSPL + Elastic License) starting with 7.11, which is a key planning consideration for self-hosted deployments. citeturn15search2turn15search2

## Tooling landscape and option comparisons

### Core open-source components with versions and licenses

The table focuses on widely used building blocks for ML-NIDS deployments and includes current versions visible in primary sources around April 2026.

| Layer | Tool | What it’s used for | Evidence of version | License evidence | Practical notes |
|---|---|---|---|---|---|
| Signature IDS/IPS | Suricata | IDS/IPS + NSM engine; produces alerts/metadata via EVE JSON | Suricata 8.0.4 listed Mar 17, 2026 citeturn22view1 | GNU GPL v2 text in repo LICENSE citeturn5view1 | EVE JSON is a common “firehose” integration point citeturn35search1 |
| Network analysis | Zeek | Protocol analyzers + rich logs (e.g., conn.log) | Zeek v8.1.1 release citeturn22view3 | Zeek COPYING is BSD 3-clause text citeturn4view0 | Good for protocol context when payload is encrypted citeturn35search2turn3search1 |
| Signature IDS | Snort 3 | Signature IDS/IPS | Snort v3.12.1.0 release citeturn22view2 | Snort LICENSE is GPL-2.0 citeturn1search4 | Uses LibDAQ for packet acquisition abstraction citeturn35search3turn35search11 |
| Flow feature extraction | CICFlowMeter | Biflow generation + >80 statistical features | CICFlowMeter repo purpose citeturn7search0 | CICFlowMeter MIT license reported citeturn38search6turn38search14 | Aligns with CIC IDS datasets feature creation citeturn7search9turn6search2 |
| Packet indexing + PCAP UI | Arkime | Large-scale PCAP capture/index + web UI | Arkime v6 release page citeturn38search7 | Apache 2.0 license citeturn19search1 | Often used for investigations and retrospective hunts citeturn18search1 |
| Event streaming | Apache Kafka | Durable ingest buffer; decouples sensors from analytics | Kafka 4.1.2 announcement citeturn15search0 | Apache 2.0 license citeturn17search0 | Useful for replay, backpressure, multi-consumer designs citeturn16search12 |
| Search/log analytics | OpenSearch | Search + dashboards for log/event analytics | OpenSearch 3.6.0 release citeturn15search5 | Apache 2.0 license file citeturn16search1 | Avoids Elastic’s SSPL/Elastic License constraints citeturn15search2 |
| Metrics/alerting | Prometheus | Metrics collection + alert rules | Prometheus v3.11.1 (Apr 7, 2026) citeturn38search4 | Apache 2.0 noted citeturn38search8 | Use for latency/throughput/drift alerting |
| Dashboards | Grafana | Visualization over metrics/logs | Grafana 12.4.2 security release citeturn38search5 | AGPLv3 license citeturn16search3turn16search7 | Licensing affects redistribution/hosted offerings |
| ML baseline library | scikit-learn | Classical ML models + preprocessing | scikit-learn 1.8.0 (Dec 9, 2025) citeturn11search4 | BSD 3-Clause citeturn11search4turn11search12 | Great for strong baselines and explainability |
| Deep learning | PyTorch | Neural models, autoencoders, transformers | torch 2.11.0 (Mar 23, 2026) citeturn12view0 | BSD-3-Clause citeturn12view0turn11search9 | Useful for sequence and representation learning |
| Deep learning | TensorFlow | Neural models; deployment tooling | tensorflow 2.21.0 (Mar 6, 2026) citeturn13view1turn13view0 | Apache 2.0 citeturn12view1turn13view1 | Strong ecosystem; versioning matters for ops |

### Architectural option comparison

| Architecture | Data input | Strengths | Weaknesses | Best fit |
|---|---|---|---|---|
| Signature-first IDS | Packet stream → rule engine | Very actionable alerts for known threats; mature; strong explainability | Limited for unknown attacks; signature maintenance burden citeturn0file0turn0search8 | Compliance-driven environments, “must block known bad” |
| Flow-based ML-NIDS | NetFlow/IPFIX or biflows | Works with encrypted payload; scalable; good for anomaly detection citeturn7search2turn7search1 | Feature extraction quality dominates; may miss app-layer specifics | Large-scale networks; cloud flow logs |
| Protocol-log ML-NIDS | Zeek/Suricata metadata logs | Rich semantic context without full DPI citeturn35search2turn35search1 | Log schema complexity; correlation effort | SOC threat hunting + ML enrichment |
| Hybrid signature + ML | Alerts + features + context | Best practical coverage; reduces false positives via correlation citeturn0search8turn35search1turn28view0 | More components; more governance | Enterprise SOC platforms and regulated orgs |

## Case studies, benchmarks, and deployment examples

### Online anomaly detection on constrained hardware: Kitsune

Kitsune positions itself as a plug-and-play NIDS using incremental statistics and an ensemble of autoencoders (KitNET) for online unsupervised anomaly detection. citeturn25view0turn28view0 Its evaluation reports multiple datasets and metrics including AUC and EER, showing how detection performance changes under different false-positive settings (e.g., FPR=0 and FPR=0.001), and compares against other anomaly detectors and a signature-based baseline. citeturn28view0turn27view1

Operational throughput results are particularly relevant for implementers: the Kitsune paper reports that, with one autoencoder, the Raspberry Pi and PC can handle approximately **~1,000** and **~7,500 packets/sec** respectively, and with an ensemble of 35 autoencoders, performance improves roughly fivefold to **~5,400** and **~37,300 packets/sec**. citeturn28view0

Why it matters in practice: these numbers illustrate that “real-time ML at the edge” is feasible when feature extraction is incremental and models are lightweight—an important design principle for branch/IoT deployments.

### IoT botnet detection with low latency: N-BaIoT

N-BaIoT targets detecting attacks launched from compromised IoT devices using deep autoencoders trained on benign traffic snapshots and then continuously monitoring for reconstruction errors. citeturn32view0turn34view0

Their empirical evaluation highlights three operationally meaningful metrics:

Detection completeness: their method detects every attack in their evaluated setup (TPR **100%**). citeturn34view0turn33view0  
False alarms: the method shows mean FPR **0.007±0.01**, lower than compared baselines (SVM, Isolation Forest, LOF). citeturn34view0turn33view0  
Time to detect: mean detection time **174±212 ms**, implying sub-second containment potential if tied to automatic isolation. citeturn34view0turn33view0

Why it matters in practice: these results provide concrete targets for “time-to-detect” engineering and emphasize per-device modeling when traffic behaviors differ (heterogeneity tolerance). citeturn32view0

### Modern deep learning IDS results on common datasets

Recent open-access studies report very high accuracy on benchmark datasets (sometimes exceeding 99%), often using transformer- or hybrid architectures. For example, a Scientific Reports paper (2024) states its model’s accuracy on NSL-KDD, CIC-DDoS 2019, and UNSW-NB15 exceeds 99%. citeturn10view0turn6search1 Another Scientific Reports study focused on SDN controller security reports a transformer model achieving **99.02% accuracy** (and CNN-LSTM 99.01%) on the InSDN dataset, also reporting feature-reduction experiments and F1/precision/recall evaluation. citeturn10view1

Practical caution: these results can be informative benchmarks, but production deployments typically face heavier drift, class imbalance, and labeling constraints than curated datasets—so treat them as capability signals rather than guaranteed outcomes. citeturn9search3turn8search2

### Production-style platforms and managed examples

Security Onion is an example of a consolidated platform approach that packages multiple tools (including Suricata and Zeek) with alerting/hunting interfaces, intended for threat hunting and enterprise security monitoring. citeturn18search4turn18search8 Its documentation notes that Elastic components and Security Onion components are under Elastic License 2.0 (ELv2), illustrating that “open platform” does not always mean “all Apache/BSD.” citeturn18search0

Cloud-native threat detection often relies on provider telemetry rather than raw packet capture. AWS GuardDuty, for example, extracts fields from log sources for profiling/anomaly detection and then discards those logs, offering a different operational model than self-hosted packet inspection. citeturn39search1 Google Cloud IDS describes a packet mirroring and inspection model within a managed peered network, illustrating a managed “mirror and inspect” pattern even when the underlying detection stack is vendor-provided. citeturn39search0

## Pitfalls, trade-offs, and mitigation strategies

### Data realism and benchmark traps

Many IDS datasets reflect specific traffic generators and labeling assumptions; CICIDS2017 and CSE-CIC-IDS2018 emphasize systematic dataset generation and feature extraction, but production traffic diversity and attack novelty remain hard to simulate fully. citeturn6search4turn7search9turn6search2 Mitigation: prioritize evaluation on (a) your own internal traffic captures and (b) red-team exercises, then use public datasets mainly for regression testing.

### False positives and analyst overload

Operational IDS success is usually constrained by false positives, because investigating alerts is expensive. Kitsune explicitly evaluates performance under extremely low FPR settings (FPR=0, 0.001) to emphasize this operational reality. citeturn28view0turn27view1 Mitigation: implement multi-stage alerting (score → threshold → correlation → escalation), and measure “alerts per analyst hour” as a first-class KPI.

### Concept drift and model decay

Traffic behavior changes due to software upgrades, new services, user behavior, and attacker adaptation. Drift-aware IDS research proposes online incremental learning and drift detection to adapt models over time. citeturn9search3turn9search11 Mitigation: implement drift monitors; maintain a “shadow model” evaluation; schedule retraining based on drift and incident feedback; align governance with NIST AI RMF lifecycle controls. citeturn8search2

### Encryption limits and feature leakage

As encryption increases, payload-based signatures weaken, pushing detection toward metadata and flow behavior. Surveys of encrypted traffic analysis discuss how ML uses timing, size, and protocol metadata patterns for classification. citeturn9search2turn9search6 Mitigation: shift feature engineering to flow/protocol patterns (SNI/JA3-like fingerprints where policy allows, connection timing, burstiness), and combine with endpoint telemetry where possible.

### Adversarial ML and training contamination

Kitsune cautions that if a NIDS trains assuming traffic is benign, a preexisting adversary can attempt to evade or poison training; it explicitly flags this as a risk and discusses training vs execute modes. citeturn28view0 Mitigation: controlled training windows, allowlisting known-good subnets during bootstrapping, multi-source validation (rules + ML), and staged rollout.

### Licensing and ecosystem constraints

Choosing “Elastic Stack” vs OpenSearch impacts licensing and operational freedom. Elastic documents the shift to SSPL + Elastic License dual licensing from Elasticsearch/Kibana 7.11 onward. citeturn15search2 Mitigation: decide early based on your redistribution/hosting posture; for internal-only deployments, you may still accept certain licenses, but document the decision.

## Effort, cost ranges, and a recommended implementation plan

This section provides realistic estimates and a step-by-step plan. Costs are highly sensitive to traffic volume, retention requirements, and whether you store PCAP vs. logs only. Where exact pricing is vendor-specific or changes frequently, this report provides **ranges with explicit assumptions** rather than brittle single-number quotes.

### Assumptions used for sizing

Traffic volumes correspond to typical deployment tiers; the system is hybrid (Suricata/Zeek + ML). Logs are retained for 30 days; PCAP retention is limited (hours–days) unless explicitly required. Models are periodically retrained. Feature extraction is flow/protocol-log based (not full DPI everywhere). This aligns with the feasibility and performance patterns shown by Kitsune and N-BaIoT and by common dataset feature pipelines (CICFlowMeter-style). citeturn28view0turn34view0turn7search1turn7search9

### Resource and cost ranges

Small deployment (single site, lab, or small business) typically covers up to ~1 Gbps mirrored traffic (often filtered). A single sensor host + a small storage node can be sufficient. Effort is commonly 4–8 person-weeks for an MVP (instrumentation, parsing, baseline model, dashboard), plus ongoing tuning. The uploaded project brief’s described stack (Python + scikit-learn + Flask/Django + web UI) is appropriate here. fileciteturn0file0turn11search4turn13view3

Medium deployment (enterprise site or multi-segment) typically requires multiple sensors, a streaming buffer (Kafka), a scalable search store (OpenSearch), and dedicated model management. Expect 3–6 months to reach production maturity with alert-quality SLAs, assuming 2–4 engineers plus SOC feedback loops.

Large deployment (multi-site, >10 Gbps aggregate, regulated SOC) generally needs sensor fleets, horizontally scalable ingestion, tiered storage (hot/warm/cold), and strong governance. Expect 6–12 months for production maturity with robust drift management and incident-response integration, and an ongoing platform team.

A practical cost breakdown (qualitative but realistic) is:

Compute grows roughly linearly with monitored throughput and feature complexity; pattern matching acceleration can materially reduce compute needs (Intel reports up to ~4× throughput improvement when using Hyperscan with Suricata in their benchmark context). citeturn37view0turn37view1  
Storage often dominates cost if you retain PCAP; log/feature retention is much cheaper than full content retention.  
People/time is often the largest “real” cost: model maintenance, false positive tuning, and response workflow integration.

### Recommended step-by-step implementation plan

Discovery and scoping: define threat goals using common taxonomies like MITRE ATT&CK (for mapping detections to tactics/techniques) and defensive countermeasure vocabulary like MITRE D3FEND. citeturn8search0turn8search3  
Telemetry bootstrap: deploy Suricata and/or Zeek on a mirrored traffic feed; enable Suricata EVE JSON; standardize Zeek logs output. citeturn35search1turn35search2  
Feature contract: define a versioned feature schema (flow + protocol + alert features). If using CIC-style features, align with CICFlowMeter-derived definitions and ensure reproducibility. citeturn7search1turn7search5  
Baseline model: start with interpretable models (e.g., Random Forest / Logistic Regression) and add anomaly models (autoencoder) if labels are limited, following the project brief’s objectives and the demonstrated effectiveness of autoencoders in Kitsune/N-BaIoT. fileciteturn0file0turn28view0turn34view0  
Evaluation: use precision/recall/F1 plus operational metrics (false positives, time-to-detect). N-BaIoT’s inclusion of detection time is a good template for operational evaluation. citeturn34view0  
Deployment: ship an inference service behind an API gateway; store results in OpenSearch and visualize in dashboards; implement alert routing to case management. citeturn15search5turn16search1turn13view3  
Operations: add monitoring (Prometheus) and dashboards (Grafana) for sensor health, ingestion lag, model latency, drift signals. citeturn38search4turn16search3  
Iterate with SOC feedback: label a small subset of alerts weekly; retrain; tune thresholds; keep a “drift + regression” dashboard.

### Implementation checklist

Use this as an execution checklist for a real deployment.

Data and collection: packet mirroring validated, loss measured; log formats standardized; time synchronization; retention policies defined. citeturn8search1turn35search1  
Security: mTLS for pipelines; least privilege; secrets rotation; signed model artifacts; audit trails aligned with continuous monitoring guidance. citeturn8search1turn8search2  
ML: feature schema versioned; training datasets versioned; offline evaluation reproducible; performance measured at low FPR regimes; drift monitors defined. citeturn28view0turn9search3  
Deployment: blue/green rollout for models; fallback to rules-only mode; alert routing tested; incident runbooks written. citeturn0search8turn8search3  
Scalability: backpressure handling via streaming; storage tiering; periodic load tests; rule engine tuned (Hyperscan enabled where applicable). citeturn17search0turn37view0turn35search0

### Selected primary sources

```text
NIST SP 800-94 (IDPS guidance): https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-94.pdf
Suricata EVE JSON output docs: https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
Zeek project (overview/licensing): https://zeek.org/about/
Kitsune (arXiv PDF): https://arxiv.org/pdf/1802.09089
N-BaIoT (arXiv PDF / IEEE Pervasive): https://arxiv.org/pdf/1805.03409
CSE-CIC-IDS2018 dataset page: https://www.unb.ca/cic/datasets/ids-2018.html
UNSW-NB15 dataset page: https://research.unsw.edu.au/projects/unsw-nb15-dataset
Apache Kafka releases: https://kafka.apache.org/blog/releases/
OpenSearch releases: https://github.com/opensearch-project/OpenSearch/releases
NIST AI RMF 1.0: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
```