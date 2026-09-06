---
document_id: rb-payment-timeout
category: runbook
service: payment
document_type: runbook
severity: high
---

# Runbook: Payment Timeout / Duplicate Charge

## Trigger

Use when:
- payment timeout rate rises
- retry rate rises
- duplicate successful charges appear
- customers report duplicate charges

## Investigation

1. Query payment attempts for the affected transaction.
2. Check whether a timeout was followed by a retry.
3. Check whether more than one attempt succeeded.
4. Inspect idempotency key presence.
5. Inspect payment retry feature flag.
6. Check provider timeout rate.
7. Search historical incidents for similar patterns.

## Strong Evidence Pattern

```text
upstream timeout
  -> automatic retry
  -> multiple successful attempts
  -> no idempotency key
```

This pattern is consistent with duplicate charge risk.

## Mitigation

- disable unsafe automatic retries
- require idempotency keys
- reconcile affected transactions
- notify billing/on-call

## Do Not

Do not assume a timeout means the provider rejected the charge.
