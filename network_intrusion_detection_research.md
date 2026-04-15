# Network Intrusion Detection System Using Machine Learning

## Project Overview

This project designs and implements a **Network Intrusion Detection System (NIDS)** using machine learning and a full-stack web architecture. The implemented prototype classifies traffic as **normal** or **malicious**, stores predictions and alerts, and provides a dashboard for monitoring, analytics, filtering, pagination, CSV export, and model evaluation.

The current implementation uses:

- `React + Vite` for the frontend dashboard
- `FastAPI` for backend APIs
- `SQLite + SQLAlchemy` for persistence
- `Python + scikit-learn` for model training and inference

Traditional security tools such as firewalls and signature-based IDS are effective for known threats but often fail against unknown or evolving attacks. A data-driven ML approach improves adaptability, detection accuracy, and operational visibility.

## Problem Statement

The rapid growth of internet services, cloud systems, and connected enterprise networks has increased exposure to cyber threats such as:

- Unauthorized access
- Malware traffic
- Denial-of-Service (DoS) behavior
- Advanced and previously unseen (zero-day) attack patterns

Conventional detection systems have limitations:

- Dependence on predefined signatures
- Difficulty detecting unknown attacks
- Higher false positive and false negative rates
- Need for frequent manual signature updates

This creates a need for an intelligent NIDS that can learn behavioral patterns from traffic data and respond to both known and unknown threats.

## Research Objectives

- Develop a machine learning based NIDS for cyber-attack detection.
- Analyze and preprocess network traffic for robust model input.
- Extract relevant features for improved classifier performance.
- Train and compare ML models for accurate intrusion classification.
- Detect both known and unknown attacks through anomaly-aware modeling.
- Reduce false alarms compared to traditional IDS pipelines.
- Provide a web-based interface for monitoring and visualization.
- Enable continuous/live packet monitoring for practical deployment.

## Scope of Work

- Deployable in organizational networks (education, healthcare, banking, cloud environments).
- Real-time analysis of network traffic streams.
- Extendable to enterprise-scale traffic loads.
- Integration-ready with existing security layers (firewalls/SIEM).
- Foundation for future deep learning based enhancements.

## Literature Context (From Project References)

The referenced works indicate active research in:

- Industrial network intrusion detection methods
- Deep and capsule network based IDS models
- Ensemble and recurrent model architectures
- Dataset creation frameworks for IDS benchmarking
- Feature clustering and correlation-based intrusion analysis

The collective trend from literature is clear: ML and DL methods can outperform static signature-only systems, especially when feature engineering and data quality are handled carefully.

## Existing System vs Proposed System

### Existing System

Existing network defense in many organizations relies on:

- Firewalls
- Antivirus tools
- Signature-based IDS

Weaknesses include:

- Low capability against unknown attack variants
- Limited adaptability to changing traffic behavior
- Inconsistent real-time detection performance

### Proposed and Implemented System

The current NIDS pipeline includes:

1. Traffic feature input through the backend API
2. Data preprocessing and protocol encoding
3. ML model training and artifact generation
4. Real-time prediction through `/predict`
5. Automatic alert generation for malicious results
6. Dashboard-based visualization of alerts, prediction history, and analytics
7. CSV export and paginated historical review
8. Model evaluation reporting from saved artifact metrics

Implemented benefits:

- Better detection visibility through a web dashboard
- Automatic alert generation for suspicious traffic
- Historical tracking of predictions and alerts
- Exportable records for academic review and reporting
- Measurable ML evaluation metrics shown in the UI

## Methodology

### 1) Data Collection

- Use benchmark intrusion datasets and/or captured traffic flows.
- Ensure representative normal and attack classes.

### 2) Data Preprocessing

- Handle missing values and noisy records.
- Encode categorical fields.
- Normalize/scale numerical features.
- Balance classes if needed (undersampling/oversampling/weights).

### 3) Feature Engineering

- Extract statistical and behavioral traffic features.
- Remove redundant and low-value features.
- Improve model signal-to-noise ratio.

### 4) Model Development

Potential baseline and comparative models:

- Logistic Regression
- Decision Tree / Random Forest
- Support Vector Machine
- Gradient Boosting variants
- (Extension) Deep learning models for complex temporal behavior

### 5) Evaluation

Primary metrics:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix analysis

Operational metrics (recommended):

- False positive rate
- False negative rate
- Inference latency for real-time readiness

### 6) Deployment

The implemented project is currently designed for local deployment and academic demonstration:

- backend started with `uvicorn`
- frontend started with `Vite`
- SQLite used for local persistence
- trained model artifact loaded from `backend/artifacts/nids_model.joblib`

The dashboard currently supports:

- authentication
- prediction submission
- alert review and resolution
- analytics timeline
- server-side filters
- CSV export
- model evaluation summary

## System Requirements

### Hardware

- Processor: Intel i3 or higher
- RAM: 4 GB minimum (8 GB recommended)
- Storage: 20 GB free space or more
- Network: Internet/LAN access for packet capture

### Software

- OS: Windows or Linux
- Frontend: `React`, `Vite`
- Backend: `FastAPI`
- Database: `SQLite`, `SQLAlchemy`
- ML Libraries: `scikit-learn`, `pandas`, `numpy`, `joblib`
- Tools: Jupyter Notebook / VS Code, optional Wireshark
- Browser: Chrome or Edge

## Implemented Outcomes

- A functional ML-based NIDS prototype capable of prediction through backend APIs
- Stored traffic, predictions, alerts, and resolution workflow
- A web dashboard for monitoring, filtering, exports, and analytics
- Persisted model evaluation metrics including accuracy, precision, recall, F1, and confusion-style counts
- A complete academic prototype that can be demonstrated end to end

## Risks and Limitations

- Model performance depends heavily on dataset quality and representativeness.
- Concept drift in real-world traffic may degrade performance over time.
- Encrypted traffic limits payload-level visibility.
- Real-time processing introduces compute and latency constraints.

## Future Enhancements

- Deep learning models for sequence-aware intrusion patterns.
- Incremental/online learning for adaptation to new threats.
- Zero-day attack discovery through advanced anomaly detection.
- Automated response integration with SIEM/SOAR ecosystems.
- Federated/distributed IDS for multi-site deployments.

## Conclusion

This project presents a practical shift from signature-only detection toward ML-driven network monitoring. The implemented system already combines training, prediction, persistence, analytics, alert handling, and UI-based monitoring in one working prototype. While the current dataset remains small and should be expanded for stronger academic credibility, the architecture and implementation now reflect a complete full-stack NIDS project rather than only a conceptual design.

## References (From Source Document)

1. Zong Xuejun, Guo Xin, He Yan, et al. Research on intrusion detection methods for industrial control networks. *Journal of Chongqing University of Technology: Natural Sciences*, 2023, 37(7): 208-216.
2. Hu Xiangdong, Li Zhihan. Industrial Internet intrusion detection method based on capsule network. *Journal of Electronics*, 2022, 50(6): 1457-1465.
3. Srinivas, M. (2013). Medical image indexing and retrieval using multiple features.
4. Li Lusheng. Research on campus network information security technology in the context of big data. *Software*, 2021, 42(10): 63-66,101.
5. Mohammadpour L, Ling TC, Liew CS, et al. A Mean Convolutional Layer for Intrusion Detection System. *Security and Communication Networks*, 2020, 2020: 1-16.
6. Dong RH, Li XY, Zhang QY, et al. Network intrusion detection model based on multivariate correlation analysis and long short-time memory network. *IET Information Security*, 2020, 14(2): 166-174.
7. Subramanian P, Ramesh GP, Parameshachari BD. Comparative analysis of machine learning approaches for early diagnosis of keratoconus. In: *Distributed Computing and Optimization Techniques: Select Proceedings of ICDCOT 2021*, 2022, pp. 241-250.
8. Aryeh FL, Alese BK, Amuzuvi CK, et al. ONDaSCA: On-demand Network Data Set Creation Application for Intrusion Detection System. *International Journal of Computer Science and Information Security*, 2020, 18(5): 111-115.
9. Olasehinde OO. A Stacked Ensemble Intrusion Detection Approach for the Protection of Information System. *Information & Security: An International Journal*, 2020, 10(1): 910-923.
10. Lakhno V, Husiev B, Blozva A, et al. Clustering network attack features in information security analysis tasks. *Cybersecurity Education Science Technique*, 2020, 1(9): 45-58.
