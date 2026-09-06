---
document_id: arch-data-flow
category: architecture
service: platform
document_type: data_flow
version: 2026.08
---

# AcmeCloud Operational Data Flow

## Request Data

A request is associated with:
- request_id
- trace_id
- user_id when authenticated
- service_id
- endpoint
- status_code
- latency_ms

The API request record is stored in the `api_requests` table.

## Payment Data

A payment record is stored in `payments`.
Each provider attempt is stored in `payment_attempts`.

Relationship:

```text
payments
   |
   +--> payment_attempts (1:N)
```

A transaction can have multiple payment attempts. Multiple successful attempts for the same
business transaction are suspicious and require investigation.

## Incident Data

An incident links to:
- affected service
- start and resolution time
- root-cause summary
- resolution
- evidence references
- timeline events

The `ground_truth_root_cause` field is evaluation-only and must never be exposed through
the production incident-investigation tool interface.

## Evidence Correlation

An investigator should correlate a hypothesis with at least two independent evidence types
where possible. Example:

```text
Hypothesis: payment retry caused duplicate charge

Evidence A: payment log shows upstream timeout + retry
Evidence B: payment_attempts shows multiple successful attempts
Evidence C: API metrics show retry rate spike
Evidence D: documentation says charge creation is non-idempotent
```
