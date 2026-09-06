---
document_id: arch-dependency-graph
category: architecture
service: platform
document_type: dependency_graph
version: 2026.08
---

# Dependency Graph and Failure Propagation

## Critical Paths

### Subscription Upgrade

```text
Client
 -> API Gateway
 -> Subscription Service
 -> Payment Service
 -> External Payment Provider
```

### Login

```text
Client
 -> API Gateway
 -> Authentication Service
 -> Signing Key / JWKS Cache
```

### Notification

```text
Application Service
 -> Notification Service
 -> Background Worker
 -> Provider
```

## Failure Propagation Rules

1. A Payment Service incident can affect Subscription Service.
2. A Subscription Service latency incident can surface as API Gateway latency.
3. A Worker backlog can surface as Notification delivery delay.
4. A stale Auth signing key can produce widespread token validation failures.
5. Rate Limit Service failure can result in both false 429 responses and protection gaps.

## Root-Cause Heuristic

When two services are abnormal, investigate the dependency direction before assuming
both services independently failed.
