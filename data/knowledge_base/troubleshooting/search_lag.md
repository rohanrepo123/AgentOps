---
document_id: ts-search-lag
category: troubleshooting
service: search
document_type: troubleshooting
---

# Troubleshooting Search Index Lag

Inspect:
- indexing queue depth
- ingestion rate
- worker concurrency
- indexing error rate
- storage errors

If query latency is normal while index age grows, investigate indexing workers rather than the query API.
