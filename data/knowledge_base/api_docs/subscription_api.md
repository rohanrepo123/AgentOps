---
document_id: api-subscription
category: api_docs
service: subscription
document_type: api
version: v3
---

# Subscription API

## POST /v1/subscriptions/upgrade

Starts a plan upgrade.

### Synchronous Work

- validate user
- validate current subscription
- calculate charge
- request payment

### Asynchronous Work

- invoice creation
- notification
- analytics event

## Timeout

The API timeout budget is 2 seconds at the gateway. Payment provider work is expected
to fit inside a 1.5 second downstream budget or return a controlled timeout state.
