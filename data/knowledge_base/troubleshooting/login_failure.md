---
document_id: ts-login-failure
category: troubleshooting
service: auth
document_type: troubleshooting
---

# Troubleshooting Login Failures

Check:
- signing-key rotation
- stale cache
- JWKS endpoint
- token validation errors
- recent auth deployment

A synchronized increase in 401 errors immediately after a key rotation strongly suggests
a signing-key propagation problem.
