# Database Connection Plan for NIDS

## Objective

Design and connect the database required for storing users, prediction records, alerts, logs, and operational metadata.

## Recommended Database

- PostgreSQL for production and academic final build
- SQLite for quick local prototype if needed

## Database Responsibilities

- Store user credentials and roles
- Store traffic metadata
- Store model predictions
- Store alert events
- Store audit and system logs
- Store model version information

## Proposed Tables

### `users`

- `id`
- `name`
- `email`
- `password_hash`
- `role_id`
- `created_at`

### `roles`

- `id`
- `role_name`

### `traffic_records`

- `id`
- `source_ip`
- `destination_ip`
- `protocol`
- `packet_size`
- `feature_payload`
- `captured_at`

### `predictions`

- `id`
- `traffic_record_id`
- `predicted_label`
- `attack_type`
- `confidence_score`
- `model_version_id`
- `predicted_at`

### `alerts`

- `id`
- `prediction_id`
- `severity`
- `status`
- `created_at`
- `resolved_at`

### `system_logs`

- `id`
- `event_type`
- `message`
- `created_at`
- `user_id`

### `model_versions`

- `id`
- `model_name`
- `version`
- `trained_on`
- `accuracy`
- `stored_path`

## Connection Layer

- Use SQLAlchemy ORM
- Use environment-based database URL
- Add migration support with Alembic

## Implementation Steps

1. Design schema.
2. Create ORM models.
3. Configure DB connection string.
4. Add migration tooling.
5. Implement repository/query functions.
6. Add indexes on `created_at`, `severity`, and `predicted_label`.
7. Test insert, fetch, update, and delete operations.

## Security Considerations

- Hash passwords before storage
- Limit direct raw queries
- Use parameterized queries
- Restrict DB access by service account
- Back up logs and alert records

## Deliverables

- Database schema
- ORM model definitions
- Migration files
- Secure connection configuration
- Query layer for backend APIs

