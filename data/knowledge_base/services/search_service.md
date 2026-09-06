---
document_id: svc-search
category: service
service: search
document_type: service_documentation
version: v3.1.4
---

# Search Service

Search requests query an index maintained by background workers.

## Important Signals

- index lag
- indexing queue depth
- query latency
- indexing error rate
- document ingestion rate

## Common Failure

High ingestion volume can cause indexing workers to fall behind, producing stale search results
while the query service itself remains healthy.
