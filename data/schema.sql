
PRAGMA foreign_keys = ON;

CREATE TABLE services (
    service_id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    owner_team TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('healthy','degraded','down')),
    region TEXT NOT NULL
);

CREATE TABLE service_dependencies (
    dependency_id INTEGER PRIMARY KEY,
    source_service TEXT NOT NULL,
    target_service TEXT NOT NULL,
    dependency_type TEXT NOT NULL CHECK(dependency_type IN ('sync','async')),
    criticality TEXT NOT NULL CHECK(criticality IN ('low','medium','high','critical')),
    timeout_ms INTEGER NOT NULL,
    FOREIGN KEY(source_service) REFERENCES services(service_id),
    FOREIGN KEY(target_service) REFERENCES services(service_id)
);

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    plan TEXT NOT NULL CHECK(plan IN ('free','pro','enterprise')),
    country TEXT NOT NULL,
    account_status TEXT NOT NULL CHECK(account_status IN ('active','suspended','deleted')),
    created_at TEXT NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan TEXT NOT NULL CHECK(plan IN ('free','pro','enterprise')),
    status TEXT NOT NULL CHECK(status IN ('active','cancelled','past_due','trial')),
    monthly_amount REAL NOT NULL,
    started_at TEXT NOT NULL,
    cancelled_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    subscription_id TEXT NOT NULL,
    transaction_id TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('SUCCESS','FAILED','PENDING','REFUNDED')),
    idempotency_key TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(subscription_id) REFERENCES subscriptions(subscription_id)
);

CREATE TABLE payment_attempts (
    attempt_id TEXT PRIMARY KEY,
    payment_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    provider_request_id TEXT NOT NULL,
    result TEXT NOT NULL CHECK(result IN ('TIMEOUT','SUCCESS','FAILED')),
    latency_ms INTEGER NOT NULL,
    error_code TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE api_requests (
    request_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    user_id TEXT,
    method TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    trace_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE metric_samples (
    sample_id INTEGER PRIMARY KEY,
    service_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT NOT NULL,
    environment TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE log_entries (
    log_id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    service_id TEXT NOT NULL,
    level TEXT NOT NULL CHECK(level IN ('DEBUG','INFO','WARN','ERROR','CRITICAL')),
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    trace_id TEXT,
    request_id TEXT,
    user_id TEXT,
    metadata_json TEXT,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE deployments (
    deployment_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    version TEXT NOT NULL,
    previous_version TEXT,
    environment TEXT NOT NULL,
    deployed_by TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('SUCCESS','FAILED','ROLLED_BACK')),
    change_summary TEXT NOT NULL,
    deployed_at TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE incidents (
    incident_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status TEXT NOT NULL CHECK(status IN ('OPEN','INVESTIGATING','RESOLVED','CLOSED')),
    affected_service TEXT NOT NULL,
    start_time TEXT NOT NULL,
    resolved_time TEXT,
    ground_truth_root_cause TEXT NOT NULL,
    resolution TEXT NOT NULL,
    FOREIGN KEY(affected_service) REFERENCES services(service_id)
);

CREATE TABLE incident_events (
    event_id INTEGER PRIMARY KEY,
    incident_id TEXT NOT NULL,
    event_time TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    source TEXT NOT NULL,
    FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE incident_evidence (
    evidence_id INTEGER PRIMARY KEY,
    incident_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL CHECK(evidence_type IN ('log','metric','database','deployment','documentation')),
    reference_id TEXT NOT NULL,
    relevance TEXT NOT NULL,
    FOREIGN KEY(incident_id) REFERENCES incidents(incident_id)
);

CREATE TABLE feature_flags (
    flag_id TEXT PRIMARY KEY,
    flag_name TEXT NOT NULL UNIQUE,
    service_id TEXT NOT NULL,
    enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
    rollout_percentage INTEGER NOT NULL CHECK(rollout_percentage BETWEEN 0 AND 100),
    updated_at TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE runbooks (
    runbook_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    service_id TEXT NOT NULL,
    trigger_condition TEXT NOT NULL,
    recommended_actions TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE INDEX idx_logs_service_time ON log_entries(service_id, timestamp);
CREATE INDEX idx_metrics_service_time ON metric_samples(service_id, recorded_at);
CREATE INDEX idx_api_service_time ON api_requests(service_id, created_at);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_attempts_payment ON payment_attempts(payment_id);
CREATE INDEX idx_incident_service ON incidents(affected_service);
CREATE INDEX idx_deployments_service_time ON deployments(service_id, deployed_at);
