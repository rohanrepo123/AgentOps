---
document_id: svc-notification
category: service
service: notification
document_type: service_documentation
version: v2.3.5
---

# Notification Service

## Responsibilities

- email
- SMS
- in-app notifications
- enqueueing asynchronous delivery jobs

## Queue Model

Notification delivery is asynchronous.

```text
Producer
  -> Notification Service
  -> Worker Queue
  -> Background Worker
  -> Provider
```

## Queue Signals

- queue depth
- oldest message age
- worker concurrency
- provider latency
- failed jobs

## Failure Pattern

A queue that grows continuously while workers remain at maximum concurrency indicates a
throughput mismatch.

Queue depth > 3,000 requires investigation.
Queue depth > 5,000 is critical for customer-facing notifications.
