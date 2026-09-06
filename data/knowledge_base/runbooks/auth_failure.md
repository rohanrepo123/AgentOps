---
document_id: rb-auth-failure
category: runbook
service: auth
document_type: runbook
severity: high
---

# Runbook: Authentication Failure

## Trigger

401/login failures rise sharply.

## Investigation

1. Check whether a signing-key rotation happened shortly before the incident.
2. Compare key cache age with current key version.
3. Inspect token validation logs.
4. Verify JWKS endpoint health.
5. Check recent authentication deployments.

## Mitigation

Refresh signing keys and invalidate stale cache entries.

## Avoid

Do not rotate credentials again unless evidence shows credential compromise.
