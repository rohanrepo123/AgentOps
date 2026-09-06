---
document_id: svc-subscription
category: service
service: subscription
document_type: service_documentation
version: v3.4.0
---

# Subscription Service

## Responsibilities

Manages:
- plan creation
- upgrades
- downgrades
- cancellation
- billing state
- payment confirmation handling

## Upgrade Flow

```text
API Gateway
  -> Subscription Service
      -> Payment Service
      -> Invoice Service
```

Payment confirmation may arrive asynchronously via Webhook Service.

## Failure Modes

### Pending Upgrade
An upgrade can remain pending if a payment confirmation webhook is delayed or lost.

### Latency
Synchronous downstream calls can consume the request timeout budget.

### Duplicate State Update
Webhook retries can produce duplicate state transitions unless updates are idempotent.

## Important Metrics

- upgrade success rate
- upgrade latency
- pending subscription count
- webhook confirmation delay
- downstream payment latency

## Recommended Practice

Independent downstream operations should be parallelized only when their dependency semantics
allow it. Never parallelize operations that have ordering requirements.
