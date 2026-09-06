---
document_id: ts-slow-api
category: troubleshooting
service: api_gateway
document_type: troubleshooting
---

# Troubleshooting Slow API

## First Question

Is the gateway slow, or is a downstream dependency slow?

## Diagnostic Sequence

1. Compare gateway latency with dependency latency.
2. Inspect endpoint-level distribution.
3. Check timeout counts.
4. Review deployments.
5. Compare CPU/memory against latency.

High latency with normal gateway CPU and high dependency latency usually points downstream.
