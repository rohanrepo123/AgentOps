from __future__ import annotations

from typing import Protocol


class QueryExpander(Protocol):
    def expand(self, query: str) -> str:
        ...


class SimpleQueryExpander:
    """
    Expands a user query with additional retrieval-oriented terminology.

    This is intentionally deterministic for the first experiment so that
    retrieval improvements can be attributed to query expansion rather than
    LLM randomness.
    """

    def expand(self, query: str) -> str:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        query = query.strip()

        expansion_terms = {
            "charged twice": (
                "duplicate payment charges payment timeout retry "
                "idempotency duplicate transaction"
            ),
            "payment timeout": (
                "payment timeout retry duplicate payment "
                "idempotency payment attempt"
            ),
            "authentication failures": (
                "authentication failure login failure key rotation "
                "API key credentials token"
            ),
            "key rotation": (
                "key rotation authentication failure credentials "
                "API key token invalid"
            ),
            "API latency": (
                "API latency slow requests downstream service "
                "dependency latency timeout bottleneck"
            ),
            "notification queues": (
                "notification queue saturation queue backlog "
                "message processing delayed consumer"
            ),
            "emails delayed": (
                "email delivery delay notification queue backlog "
                "email worker consumer"
            ),
            "subscription upgrades": (
                "subscription upgrade pending payment processing "
                "state transition dependency"
            ),
            "webhook delivery failures": (
                "webhook delivery failure retry timeout "
                "downstream endpoint response"
            ),
            "stale search results": (
                "search stale results indexing cache synchronization "
                "search index refresh"
            ),
            "object storage upload failures": (
                "object storage upload failure timeout storage "
                "upload retry permission"
            ),
            "429 responses": (
                "HTTP 429 rate limiting throttling "
                "request limit API rate limiter"
            ),
        }

        query_lower = query.lower()

        matched_terms: list[str] = []

        for phrase, expansion in expansion_terms.items():
            if phrase.lower() in query_lower:
                matched_terms.append(expansion)

        if not matched_terms:
            return query

        return f"{query} {' '.join(matched_terms)}"