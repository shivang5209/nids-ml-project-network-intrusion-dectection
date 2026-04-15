# NIDS Research Adapted for Project Implementation

## Purpose

This document extracts the most useful parts of the deep research report and adapts them to the actual scope of this project.

The original deep research is technically strong, but it mixes:

- enterprise-grade SOC architecture,
- managed/cloud security platform ideas,
- broken citation tokens,
- and tool choices that are too heavy for the current academic implementation.

This version keeps the strongest research conclusions and turns them into a practical build direction for this project.

## Core Research Conclusion

The strongest conclusion from the research is this:

An effective Network Intrusion Detection System should not be treated as only a classifier. The real system is a pipeline that:

1. collects network telemetry,
2. converts it into usable features,
3. applies machine learning for classification or anomaly detection,
4. stores prediction and alert results,
5. displays them through a usable monitoring interface,
6. and continuously improves through retraining and review.

That is the right engineering mindset for this project.

## Best Technical Direction for This Project

For this project, the most practical architecture is:

- Frontend: `React + Vite`
- Backend: `FastAPI`
- Database: `PostgreSQL`
- ML layer: `Python + scikit-learn + joblib`

This stack is the best balance between:

- implementation speed,
- flexibility,
- ML integration,
- academic presentation quality,
- and future extensibility.

## What We Should Keep From the Deep Research

### 1. Think in Terms of Pipeline, Not Just Model

The deep research correctly emphasizes that the real challenge is not choosing a classifier alone. The harder and more important part is building:

- telemetry flow,
- feature extraction,
- inference,
- alert generation,
- monitoring,
- and model lifecycle management.

This should shape the project architecture.

### 2. Use Flow/Metadata-Based Detection for the Main Build

The report explains that modern traffic is often encrypted, which limits payload-based inspection. For this project, that means the ML model should mainly rely on:

- flow statistics,
- packet counts,
- protocol metadata,
- timing information,
- source/destination behavior,
- and engineered traffic features.

This is a better project choice than attempting full payload inspection.

### 3. Start With Interpretable Baseline Models

The report supports starting with classical ML models before using deep learning. That is the right move here.

Best baseline models for this project:

- Logistic Regression
- Decision Tree
- Random Forest
- Support Vector Machine
- Gradient Boosting

These are easier to train, explain, compare, and present in an academic setting.

### 4. Evaluate Beyond Accuracy

One of the best insights in the research is that real intrusion detection quality depends on more than accuracy.

For this project, the evaluation must include:

- Accuracy
- Precision
- Recall
- F1-score
- False positive rate
- False negative rate
- Confusion matrix
- Inference latency

This is important because IDS systems fail in practice when false alarms become too high.

### 5. Plan for Drift and Model Updating

The research correctly highlights concept drift. Network behavior changes over time, so an ML-based IDS must not be treated as a train-once system.

For this project, that means:

- model version should be stored,
- predictions should be logged,
- suspicious or incorrect results should be reviewable,
- retraining should be supported later.

Even if full drift automation is not implemented now, the system should be designed so it can be added later.

## What We Should Not Adopt Directly Right Now

The deep research includes strong ideas, but several of them are too heavy for the current project stage.

### Not needed for MVP

- Kafka or event streaming bus
- OpenSearch or ClickHouse
- SIEM/SOAR integration
- Prometheus and Grafana as mandatory dependencies
- Blue/green model rollout
- Multi-sensor enterprise deployment
- Suricata + Zeek + packet mirroring as a hard requirement

These are good future-extension ideas, but they should not define the first implementation.

## Practical Architecture for This Project

## System Flow

The recommended execution flow is:

1. User opens the frontend dashboard.
2. Frontend sends request to backend.
3. Backend accepts traffic feature input or stored dataset input.
4. Backend loads the trained model.
5. Backend runs prediction.
6. Prediction result is stored in the database.
7. If malicious, an alert is generated.
8. Frontend displays the alert, prediction result, and monitoring summary.

## Module Design

### Frontend

Use React to build:

- login page,
- dashboard,
- live monitoring panel,
- alerts page,
- reports page,
- settings/admin page.

### Backend

Use FastAPI to provide:

- authentication routes,
- prediction route,
- traffic upload route,
- alerts route,
- reports route,
- health route.

### Database

Use PostgreSQL for:

- users,
- roles,
- traffic records,
- predictions,
- alerts,
- system logs,
- model versions.

### ML Layer

Use Python for:

- dataset preprocessing,
- feature engineering,
- model training,
- model evaluation,
- model export with `joblib`,
- prediction inference from backend.

## Recommended Detection Strategy

The deep research argues for hybrid systems in real deployments. For this project, the best adaptation is:

### MVP strategy

- Build an ML-based NIDS using dataset-derived network features.
- Focus on classification of traffic as normal or malicious.
- Optionally classify attack category if labels exist.

### Future hybrid strategy

After the MVP works, the project can be extended with:

- Suricata for signature alerts,
- Zeek for rich protocol logs,
- ML model for anomaly scoring,
- combined alert correlation.

This is the cleanest way to benefit from the research without overbuilding now.

## Recommended Dataset Direction

The research mentions the value of flow-based datasets and reproducible feature extraction.

Recommended datasets for this project:

- NSL-KDD
- CIC-IDS2017
- UNSW-NB15

Selection advice:

- Use `NSL-KDD` if you want a simpler academic baseline.
- Use `CIC-IDS2017` if you want more modern traffic variety.
- Use `UNSW-NB15` if you want a more realistic modern benchmark.

Best practical choice:

- Start model experiments with `NSL-KDD`
- move to `CIC-IDS2017` if time permits

## Feature Strategy

One of the best implementation ideas in the deep research is the concept of a feature contract.

For this project, define a stable input schema for the model. Example fields can include:

- source IP
- destination IP
- source port
- destination port
- protocol
- packet count
- byte count
- flow duration
- average packet size
- packets per second
- bytes per second
- SYN count / flag patterns where available

This matters because:

- backend and ML must agree on input format,
- retraining becomes easier,
- inference becomes reproducible,
- future integration with live traffic becomes simpler.

## Recommended Evaluation Strategy

The deep research is correct that benchmark numbers alone are not enough.

For this project, evaluation should be done in two layers:

### Offline model evaluation

- train/test split metrics,
- confusion matrix,
- comparison across models,
- best model selection.

### System evaluation

- time to get prediction from backend,
- whether malicious predictions create alerts correctly,
- whether dashboard reflects new results,
- whether false positives are manageable in sample runs.

This makes the project more complete than a notebook-only ML demo.

## Security Implications We Should Carry Forward

The research strongly reinforces that the NIDS itself is security-sensitive infrastructure.

Minimum controls to keep in this project:

- password hashing,
- role-based access control,
- request validation,
- rate limiting on sensitive routes,
- audit logs,
- secure storage of model files,
- environment-based secret management.

These controls are enough for the current implementation and align with the earlier security documents we created.

## Recommended Build Priority

Based on both the deep research and the actual project scope, the build order should be:

1. Finalize frontend stack and UI structure
2. Prepare dataset and define feature schema
3. Train baseline ML models
4. Create backend inference API
5. Connect PostgreSQL for users, predictions, and alerts
6. Connect frontend to backend
7. Add alert and reporting flow
8. Add security controls
9. Test the full project end to end

This is the most realistic path from research to working system.

## Final Recommendation

The best outcome from the deep research is not to copy its full enterprise architecture. The best outcome is to apply its strongest lessons in a smaller, cleaner system.

The right implementation strategy for this project is:

- Build a full-stack ML-based NIDS first
- Use interpretable ML baselines
- Use flow/metadata-oriented features
- Measure false positives and latency, not only accuracy
- Store model outputs and alerts cleanly
- Keep the architecture extensible for future hybrid IDS integration

That gives this project both academic strength and practical engineering quality.

## Selected Reference Links from the Deep Research

These links are the most useful ones to keep for implementation and report writing:

- NIST SP 800-94: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-94.pdf
- NIST AI RMF 1.0: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
- Suricata EVE JSON output docs: https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- Zeek overview: https://zeek.org/about/
- Kitsune paper: https://arxiv.org/pdf/1802.09089
- N-BaIoT paper: https://arxiv.org/pdf/1805.03409
- CSE-CIC-IDS2018 dataset: https://www.unb.ca/cic/datasets/ids-2018.html
- UNSW-NB15 dataset: https://research.unsw.edu.au/projects/unsw-nb15-dataset

