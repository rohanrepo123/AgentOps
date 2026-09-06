---
document_id: svc-payment
category: service
service: payment
document_type: service_documentation
version: v2.8.1
---

# Payment Service

## Responsibilities

The Payment Service handles:
- charge creation
- refunds
- payment status
- payment provider communication
- payment retries
- reconciliation

## Charge Creation

Endpoint: `POST /v1/payments/charge`

Charge creation is **not idempotent by default**.

Clients and internal services must provide an idempotency key when an operation may be retried.

### Safe Retry Policy

| Operation | Retry? | Requirement |
|---|---|---|
| Read payment status | Yes | bounded retries |
| Create charge | No by default | idempotency key required |
| Refund | Conditional | provider idempotency supported |
| Reconcile | Yes | safe/idempotent operation |

## Payment Attempt Semantics

Every call to the payment provider is recorded in `payment_attempts`.

An upstream timeout does not imply the provider did not process the request.

Therefore:

> Never blindly retry a timed-out charge creation without an idempotency key.

## Important Metrics

- `payment_request_rate`
- `payment_error_rate`
- `payment_retry_rate`
- `payment_p95_latency`
- `payment_provider_timeout_rate`
- `payment_duplicate_charge_rate`

## Warning Thresholds

- retry rate > 5% for 5 minutes: investigate
- error rate > 5% for 5 minutes: investigate
- p95 latency > 2 seconds: investigate
- duplicate charge signal > baseline: high priority

## Relevant Data

Database tables:
- `payments`
- `payment_attempts`

Relevant feature flags:
- `flag-payment-retry`
- `flag-payment-idempotency`

Relevant runbook:
- `RB-PAY-001`
