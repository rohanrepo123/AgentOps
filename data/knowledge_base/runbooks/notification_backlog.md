---
document_id: rb-notification-backlog
category: runbook
service: notification
document_type: runbook
severity: medium
---

# Runbook: Notification Queue Backlog

## Trigger

Email queue depth > 3,000 or oldest message age exceeds 10 minutes.

## Investigation

1. Check queue depth trend.
2. Check worker concurrency.
3. Inspect provider latency/errors.
4. Check recent deployments.
5. Determine whether producer traffic increased.

## Mitigation

- increase worker concurrency when safe
- address provider bottlenecks
- configure queue backpressure
- protect critical notifications from starvation
