---
document_id: api-payment
category: api_docs
service: payment
document_type: api
version: v2
---

# Payment API

## POST /v1/payments/charge

Creates a charge.

### Request

```json
{
  "user_id": "usr-0001",
  "amount": 49.00,
  "currency": "USD",
  "idempotency_key": "idem-123"
}
```

### Response

```json
{
  "transaction_id": "txn-100500",
  "status": "SUCCESS"
}
```

### Idempotency

`idempotency_key` is strongly recommended for charge creation.

Requests without an idempotency key must not be automatically retried after an ambiguous
provider response.

### Errors

- 400 invalid request
- 401 unauthorized
- 409 duplicate/idempotency conflict
- 429 rate limited
- 500 internal failure
- 502 provider failure
- 504 provider timeout
