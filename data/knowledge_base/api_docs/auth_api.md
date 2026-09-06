---
document_id: api-auth
category: api_docs
service: auth
document_type: api
version: v4
---

# Authentication API

## POST /v1/login

Returns access and refresh tokens after credential validation.

## GET /v1/.well-known/jwks.json

Returns the current public signing keys.

Clients must treat 401 spikes after key rotation as an operational signal when the failure begins
immediately after rotation.
