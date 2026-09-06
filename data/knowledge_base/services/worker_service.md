---
document_id: svc-worker
category: service
service: worker
document_type: service_documentation
version: v1.9.7
---

# Background Worker

The worker executes asynchronous jobs for notifications, analytics, reconciliation and webhook processing.

## Key Metrics

- queue depth
- oldest job age
- jobs per minute
- worker utilization
- job failure rate
- retry count

## Saturation

A worker pool is considered saturated when queue depth rises continuously while workers operate
near maximum concurrency.

Scaling workers without checking downstream provider capacity can move the bottleneck downstream.
