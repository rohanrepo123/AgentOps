---
document_id: rb-api-latency
category: runbook
service: api_gateway
document_type: runbook
severity: medium
---

# Runbook: API Latency

## Trigger

P95 latency > 2 seconds for 5 minutes or a sustained increase in timeout rate.

## Investigation

1. Check gateway p50/p95/p99.
2. Break down latency by endpoint.
3. Inspect downstream service latency.
4. Check recent deployments.
5. Inspect CPU/memory only after dependency latency has been considered.
6. Identify independent downstream calls that can safely run concurrently.

## Common Root Cause

A synchronous dependency exceeds its expected latency budget and consumes upstream request capacity.

## Mitigation

- enforce downstream timeouts
- reduce unnecessary sequential work
- parallelize independent calls
- roll back a recent problematic deployment when evidence supports it
