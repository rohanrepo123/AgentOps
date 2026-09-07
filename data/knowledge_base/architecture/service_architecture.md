---
document_id: arch-service-architecture
category: architecture
service: platform
related_services: rate-limit
document_type: service_architecture
version: 2026.08
---

# Service Architecture

## Dependency Graph

```text
API Gateway
 ├── Auth Service
 ├── User Service
 ├── Subscription Service
 │     ├── Payment Service
 │     └── Invoice Service (async)
 ├── Search Service
 │     └── Storage Service
 └── Rate Limit Service

Payment Service
 ├── Configuration Service
 └── Webhook Service (async)

Webhook Service
 └── Background Worker

Notification Service
 └── Background Worker

Analytics Service
 └── Background Worker
```

## Dependency Criticality

### Critical
- API Gateway -> Authentication
- API Gateway -> Subscription
- Subscription -> Payment
- Payment -> provider
- Webhook -> Worker for durable asynchronous processing

### High
- API Gateway -> User
- Subscription -> Invoice
- Notification -> Worker
- Payment -> Webhook

### Medium/Low
- Search -> Storage
- Analytics -> Worker

## Timeout Budgets

| Dependency | Default Timeout |
|---|---:|
| Auth | 500 ms |
| Rate Limit | 150 ms |
| User | 700 ms |
| Subscription | 1000 ms |
| Payment | 1500 ms |
| Search | 800 ms |
| Storage | 1000 ms |

Timeouts are budgets, not targets. A healthy dependency should normally respond well
below its timeout.

## Common Failure Patterns

### Cascading latency
A slow downstream service can consume upstream request threads and cause timeouts in services
that are otherwise healthy.

### Retry amplification
Retries can multiply load during an outage. This is especially dangerous for non-idempotent
operations such as payment charge creation.

### Queue saturation
Asynchronous systems degrade when producer throughput exceeds worker throughput for a sustained
period.

### Stale configuration
Cached configuration, signing keys, and feature flags can survive longer than their intended
validity period.
