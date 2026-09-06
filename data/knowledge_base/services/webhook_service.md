---
document_id: svc-webhook
category: service
service: webhook
document_type: service_documentation
version: v2.6.2
---

# Webhook Service

## Responsibilities

- receive provider callbacks
- validate signatures
- persist events
- schedule processing
- retry transient failures

## Retry Policy

Retry transient errors such as:
- 408
- 429
- 500
- 502
- 503
- connection timeout

Do not retry indefinitely.

## Idempotency

Webhook event IDs must be deduplicated before applying state changes.

## Metrics

- webhook success rate
- delivery latency
- retry count
- queue depth
- duplicate-event count
