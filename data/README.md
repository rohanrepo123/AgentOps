# AcmeCloud Full Phase-1 Synthetic Production Dataset

A synthetic SaaS production environment for the AgentOps incident-investigation agent.

The dataset is intentionally cross-linked across services, users, payments, logs,
metrics, deployments, feature flags, runbooks, incidents and incident evidence.

Benchmark case:
INC-001 / txn-100500 represents a duplicate-payment incident caused by a
non-idempotent retry after an upstream timeout.

The ground-truth fields in `incidents` are for offline evaluation and should not
be exposed to the agent's investigation tools in production mode.
