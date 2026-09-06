---
document_id: arch-system-overview
category: architecture
service: platform
document_type: system_overview
version: 2026.08
---

# AcmeCloud System Overview

AcmeCloud is a multi-tenant SaaS platform used by customers to manage subscriptions, invoices,
payments, team accounts, API integrations, search, document storage, and notifications.

## High-Level Request Path

External clients enter through the API Gateway.

```text
Client
  |
  v
API Gateway
  |
  +--> Authentication Service
  +--> User Service
  +--> Subscription Service
  +--> Search Service
  +--> Webhook Service
```

Subscription operations may synchronously invoke the Payment Service. Invoice creation is normally
asynchronous and is handled by Background Worker and Invoice Service.

## Core Services

| Service | ID | Responsibility |
|---|---|---|
| API Gateway | svc-api | Request routing, auth enforcement, rate limiting |
| Authentication | svc-auth | Login, token validation, signing key management |
| User | svc-user | Profiles and account state |
| Subscription | svc-subscription | Plans, upgrades, downgrades |
| Payment | svc-payment | Charges, refunds, provider interaction |
| Invoice | svc-invoice | Invoice generation |
| Notification | svc-notification | Email/SMS/in-app notifications |
| Worker | svc-worker | Async jobs |
| Search | svc-search | Search/indexing |
| Storage | svc-storage | File/object storage |
| Webhook | svc-webhook | Webhook ingestion and delivery |
| Analytics | svc-analytics | Usage event processing |
| Configuration | svc-config | Feature flags and runtime configuration |
| Rate Limit | svc-rate-limit | Distributed request limiting |

## Reliability Principles

1. Charge creation must be idempotent.
2. Retry only operations known to be safe to retry.
3. External dependencies must have bounded timeouts.
4. Asynchronous work must have queue-depth monitoring.
5. Configuration and feature-flag changes must be auditable.
6. Incident conclusions must be supported by multiple independent evidence sources.

## Investigation Guidance

For an incident, engineers should correlate:
- application logs
- service metrics
- deployment history
- feature flags
- database records
- relevant runbooks
- historical incidents

A single anomalous log line is not sufficient to establish root cause.
