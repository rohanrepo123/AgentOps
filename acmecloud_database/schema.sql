
PRAGMA foreign_keys = ON;

CREATE TABLE services (
    service_id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    owner_team TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'down')),
    version TEXT NOT NULL
);

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'pro', 'enterprise')),
    country TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'pro', 'enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'past_due')),
    monthly_amount REAL NOT NULL,
    started_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    subscription_id TEXT NOT NULL,
    transaction_id TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'PENDING', 'REFUNDED')),
    idempotency_key TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);

CREATE TABLE payment_attempts (
    attempt_id TEXT PRIMARY KEY,
    payment_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    provider_request_id TEXT NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('TIMEOUT', 'SUCCESS', 'FAILED')),
    latency_ms INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE incidents (
    incident_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    affected_service TEXT NOT NULL,
    ground_truth_root_cause TEXT NOT NULL,
    resolution TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (affected_service) REFERENCES services(service_id)
);
