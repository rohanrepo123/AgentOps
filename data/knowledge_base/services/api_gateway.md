---
document_id: svc-api
category: service
service: api_gateway
document_type: service_documentation
version: v5.2.0
---

# API Gateway

## Responsibilities

- routing
- authentication enforcement
- rate limiting
- request timeout enforcement
- request tracing

## Latency Decomposition

For an API request:

```text
Gateway latency =
routing
+ auth
+ downstream service time
+ serialization
+ network overhead
```

If a downstream synchronous dependency is slow, gateway p95 may increase even when the
gateway itself has low CPU usage.

## Important Signals

- p50 / p95 / p99 latency
- 4xx rate
- 5xx rate
- timeout rate
- downstream latency by service
- requests per minute

## Investigation Rule

For elevated gateway latency, inspect dependency latency and recent gateway deployments
before scaling the gateway itself.
