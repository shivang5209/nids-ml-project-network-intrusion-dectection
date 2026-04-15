# Threat Model for NIDS Project

## Objective

This document identifies the main threats, attack surfaces, and controls for the Network Intrusion Detection System project.

## System Assets

- User accounts
- Model files
- Prediction records
- Alert history
- Traffic metadata
- Backend APIs
- Database contents
- Admin settings

## Threat Actors

- Unauthorized external attacker
- Insider with misuse intent
- Malicious user with stolen credentials
- Adversary attempting model evasion

## Entry Points

- Login page
- Prediction API
- Traffic upload API
- Admin routes
- Database connection
- Model artifact storage

## Major Threats

### 1. Unauthorized Access

- Attackers attempt login bypass or credential theft.
- Risk: high
- Controls:
  - Strong password policy
  - Password hashing
  - JWT/session expiry
  - Role-based access control

### 2. API Abuse

- Attackers flood prediction or auth endpoints.
- Risk: high
- Controls:
  - Rate limiting
  - Input validation
  - Logging and alerting

### 3. Data Injection or Malformed Input

- Malicious inputs cause backend failure or stored corruption.
- Risk: medium
- Controls:
  - Schema validation
  - Parameterized queries
  - Sanitization

### 4. Model Evasion

- Adversary crafts traffic to avoid detection.
- Risk: high
- Controls:
  - Threshold review
  - Ensemble models
  - Retraining with new patterns
  - Monitoring of suspicious low-confidence predictions

### 5. Data Poisoning

- Compromised training data reduces model reliability.
- Risk: medium
- Controls:
  - Verified dataset sources
  - Dataset checksums
  - Review before retraining

### 6. Sensitive Data Exposure

- Logs or database expose sensitive operational details.
- Risk: high
- Controls:
  - Least privilege access
  - Secure backups
  - Sensitive field review

### 7. Alert Manipulation

- Adversary marks alerts resolved or hides incidents.
- Risk: medium
- Controls:
  - Admin-only alert updates
  - Audit logging
  - Immutable event history where possible

## Security Priorities

- Protect authentication
- Secure APIs
- Protect model integrity
- Preserve alert accuracy
- Maintain audit trail

## Deliverables

- Threat list with controls
- Risk classification table
- Security review reference for implementation

