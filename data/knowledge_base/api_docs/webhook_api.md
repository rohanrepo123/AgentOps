---
document_id: api-webhook
category: api_docs
service: webhook
document_type: api
version: v2
---

# Webhook API

## POST /v1/webhooks/payment

Receives payment-provider events.

### Required Headers

- `X-Signature`
- `X-Event-ID`
- `X-Provider`

### Processing

1. verify signature
2. deduplicate event ID
3. persist event
4. acknowledge
5. process asynchronously when possible

### Duplicate Event Handling

Receiving the same event ID more than once must not produce multiple business-state transitions.
