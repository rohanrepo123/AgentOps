from __future__ import annotations

from typing import Protocol


class MultiQueryExpanderProtocol(Protocol):
    def expand(self, query: str) -> list[str]:
        ...


class MultiQueryExpander:
    """
    Generates multiple retrieval-oriented query variants.

    The original query is always preserved as the first query.
    Variants are intentionally deterministic for reproducible
    retrieval experiments.
    """

    def expand(self, query: str) -> list[str]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        query = query.strip()

        query_lower = query.lower()

        variants: list[str] = [query]

        expansion_rules = [
            (
                "charged twice",
                [
                    f"{query} duplicate payment transaction",
                    f"{query} payment retry idempotency",
                    f"{query} duplicate charge payment attempt",
                ],
            ),
            (
                "payment timeout",
                [
                    f"{query} payment retry timeout",
                    f"{query} payment attempt idempotency",
                    f"{query} duplicate transaction timeout",
                ],
            ),
            (
                "authentication failures",
                [
                    f"{query} authentication login credentials failure",
                    f"{query} API key token invalid",
                    f"{query} authentication configuration key rotation",
                ],
            ),
            (
                "key rotation",
                [
                    f"{query} API key rotation authentication",
                    f"{query} invalid credentials authentication failure",
                    f"{query} token credentials service authentication",
                ],
            ),
            (
                "API latency",
                [
                    f"{query} slow API requests downstream dependency",
                    f"{query} service dependency latency timeout",
                    f"{query} API performance bottleneck downstream service",
                ],
            ),
            (
                "notification queues",
                [
                    f"{query} notification queue backlog",
                    f"{query} message consumer processing delay",
                    f"{query} queue saturation worker processing",
                ],
            ),
            (
                "emails delayed",
                [
                    f"{query} email delivery notification queue",
                    f"{query} email worker consumer backlog",
                    f"{query} notification processing delay",
                ],
            ),
            (
                "subscription upgrades",
                [
                    f"{query} subscription upgrade payment processing",
                    f"{query} subscription state transition",
                    f"{query} upgrade dependency payment state",
                ],
            ),
            (
                "webhook delivery failures",
                [
                    f"{query} webhook retry timeout downstream endpoint",
                    f"{query} webhook delivery failure response",
                    f"{query} webhook endpoint availability retry",
                ],
            ),
            (
                "stale search results",
                [
                    f"{query} search index stale results",
                    f"{query} indexing refresh synchronization",
                    f"{query} search cache index consistency",
                ],
            ),
            (
                "object storage upload failures",
                [
                    f"{query} object storage upload timeout",
                    f"{query} storage upload retry permission",
                    f"{query} object storage failure connectivity",
                ],
            ),
            (
                "429 responses",
                [
                    f"{query} HTTP 429 rate limiting",
                    f"{query} API throttling request limit",
                    f"{query} rate limiter request rejection",
                ],
            ),
        ]

        for phrase, rule_variants in expansion_rules:
            if phrase in query_lower:
                variants.extend(rule_variants)
                break

        # Remove accidental duplicates while preserving order.
        deduplicated: list[str] = []
        seen: set[str] = set()

        for variant in variants:
            normalized = variant.strip().lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            deduplicated.append(variant.strip())

        return deduplicated