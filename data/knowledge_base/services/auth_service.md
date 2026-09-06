---
document_id: svc-auth
category: service
service: auth
document_type: service_documentation
version: v4.1.2
---

# Authentication Service

## Responsibilities

- password authentication
- token validation
- signing key rotation
- session management

## Signing Key Rotation

Authentication validates tokens using a cached key set.

After a key rotation, the service must:
1. refresh signing keys
2. invalidate obsolete entries
3. tolerate propagation during a bounded transition period

## Failure Pattern

A stale signing-key cache may cause:
- token validation failures
- login failures
- elevated 401 responses

## Relevant Metrics

- token validation failure rate
- login failure rate
- key refresh failures
- cache age

## Diagnostic Rule

When authentication errors spike immediately after a signing-key rotation, inspect
the signing-key cache before changing user credentials or token generation.
