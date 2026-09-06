---
document_id: svc-invoice
category: service
service: invoice
document_type: service_documentation
version: v2.5.3
---

# Invoice Service

Invoices are generated from subscription and payment records.

## Important Integrity Rule

An invoice should not be marked paid until the corresponding payment is confirmed.

## Common Failures

- malformed tax metadata
- missing billing address
- stale subscription state
- delayed payment confirmation

## Diagnostic Sources

- `payments`
- `subscriptions`
- invoice logs
- webhook events
