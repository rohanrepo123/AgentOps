---
document_id: rb-webhook-failure
category: runbook
service: webhook
document_type: runbook
severity: high
---

# Runbook: Webhook Delivery Failure

## Trigger

Webhook failure rate > 5%.

## Investigation

1. Inspect response codes.
2. Separate transient from permanent failures.
3. Check worker queue depth.
4. Search logs by event ID.
5. Verify deduplication behavior.
6. Check recent deployments.

## Mitigation

Retry transient failures with bounded exponential backoff and route persistent failures
to a dead-letter queue.
