from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from langchain_core.tools import tool


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "acmecloud.db"


# ---------------------------------------------------------------------
# Allowed entities
# ---------------------------------------------------------------------

ALLOWED_ENTITIES = {
    "services",
    "service_dependencies",
    "users",
    "subscriptions",
    "payments",
    "payment_attempts",
    "api_requests",
    "metric_samples",
    "log_entries",
    "deployments",
    "incidents",
    "incident_events",
    "incident_evidence",
    "feature_flags",
    "runbooks",
}


# ---------------------------------------------------------------------
# Exposed columns
# ---------------------------------------------------------------------
# Keep explicit projections instead of SELECT *.
#
# IMPORTANT:
# incidents.ground_truth_root_cause and incidents.resolution
# are intentionally NOT exposed to the live investigation agent.
# They are evaluation-only fields.
# ---------------------------------------------------------------------

ENTITY_COLUMNS: dict[str, list[str]] = {
    "services": [
        "service_id",
        "service_name",
        "description",
        "owner_team",
        "version",
        "status",
        "region",
    ],
    "service_dependencies": [
        "dependency_id",
        "source_service",
        "target_service",
        "dependency_type",
        "criticality",
        "timeout_ms",
    ],
    "users": [
        "user_id",
        "email",
        "first_name",
        "last_name",
        "plan",
        "country",
        "account_status",
        "created_at",
    ],
    "subscriptions": [
        "subscription_id",
        "user_id",
        "plan",
        "status",
        "monthly_amount",
        "started_at",
        "cancelled_at",
    ],
    "payments": [
        "payment_id",
        "user_id",
        "subscription_id",
        "transaction_id",
        "amount",
        "currency",
        "provider",
        "status",
        "idempotency_key",
        "created_at",
    ],
    "payment_attempts": [
        "attempt_id",
        "payment_id",
        "attempt_number",
        "provider_request_id",
        "result",
        "latency_ms",
        "error_code",
        "created_at",
    ],
    "api_requests": [
        "request_id",
        "service_id",
        "user_id",
        "method",
        "endpoint",
        "status_code",
        "latency_ms",
        "trace_id",
        "created_at",
    ],
    "metric_samples": [
        "sample_id",
        "service_id",
        "metric_name",
        "metric_value",
        "unit",
        "environment",
        "recorded_at",
    ],
    "log_entries": [
        "log_id",
        "timestamp",
        "service_id",
        "level",
        "event_type",
        "message",
        "trace_id",
        "request_id",
        "user_id",
        "metadata_json",
    ],
    "deployments": [
        "deployment_id",
        "service_id",
        "version",
        "previous_version",
        "environment",
        "deployed_by",
        "status",
        "change_summary",
        "deployed_at",
    ],
    "incidents": [
        "incident_id",
        "title",
        "description",
        "severity",
        "status",
        "affected_service",
        "start_time",
        "resolved_time",
    ],
    "incident_events": [
        "event_id",
        "incident_id",
        "event_time",
        "event_type",
        "description",
        "source",
    ],
    "incident_evidence": [
        "evidence_id",
        "incident_id",
        "evidence_type",
        "reference_id",
        "relevance",
    ],
    "feature_flags": [
        "flag_id",
        "flag_name",
        "service_id",
        "enabled",
        "rollout_percentage",
        "updated_at",
    ],
    "runbooks": [
        "runbook_id",
        "title",
        "service_id",
        "trigger_condition",
        "recommended_actions",
        "last_updated",
    ],
}


# ---------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_database_path() -> Path:
    """Return the AcmeCloud SQLite database path."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"AcmeCloud database not found at: {DATABASE_PATH}"
        )

    return DATABASE_PATH


def _connect() -> sqlite3.Connection:
    """
    Open a read-only SQLite connection.

    The investigation system must not modify production-like data.
    """

    database_path = _get_database_path()

    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro",
        uri=True,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------

def _validate_entity(entity: str) -> None:
    """Validate that the requested entity is explicitly supported."""

    if entity not in ALLOWED_ENTITIES:
        raise ValueError(
            f"Unsupported entity '{entity}'. "
            f"Allowed entities: {sorted(ALLOWED_ENTITIES)}"
        )


def _validate_limit(limit: int) -> int:
    """Validate and cap the result limit."""

    if limit <= 0:
        raise ValueError(
            "limit must be greater than 0."
        )

    # Prevent an agent from requesting thousands of rows.
    return min(limit, 100)


def _build_filter_clause(
    filters: Optional[dict[str, Any]],
    allowed_columns: set[str],
) -> tuple[str, list[Any]]:
    """
    Build a parameterized equality-based WHERE clause.

    Example:

        {
            "status": "FAILED",
            "provider": "stripe"
        }

    becomes:

        WHERE "status" = ? AND "provider" = ?

    Values are passed separately to SQLite to avoid SQL injection.
    """

    if not filters:
        return "", []

    conditions: list[str] = []
    values: list[Any] = []

    for column, value in filters.items():

        if column not in allowed_columns:
            raise ValueError(
                f"Invalid filter column '{column}'."
            )

        # Keep the first version deliberately simple and deterministic.
        if isinstance(value, (dict, list, tuple, set)):
            raise ValueError(
                f"Unsupported filter value for column '{column}'."
            )

        conditions.append(
            f'"{column}" = ?'
        )
        values.append(value)

    return (
        " WHERE " + " AND ".join(conditions),
        values,
    )


def _format_rows(
    entity: str,
    columns: list[str],
    rows: list[sqlite3.Row],
) -> str:
    """Convert database rows into an LLM-readable response."""

    if not rows:
        return (
            f"No records found in '{entity}' "
            "matching the supplied filters."
        )

    output = [
        f"Entity: {entity}",
        f"Rows returned: {len(rows)}",
        "",
    ]

    for index, row in enumerate(rows, start=1):

        output.append(
            f"[Record {index}]"
        )

        for column in columns:
            output.append(
                f"{column}: {row[column]}"
            )

        output.append("")

    return "\n".join(output)


# ---------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------

@tool
def query_database(
    entity: str,
    filters: Optional[dict[str, Any]] = None,
    limit: int = 20,
) -> str:
    """
    Query approved AcmeCloud operational data.

    This tool provides controlled, read-only access to selected
    database entities.

    Supported entities:
    - services
    - service_dependencies
    - users
    - subscriptions
    - payments
    - payment_attempts
    - api_requests
    - metric_samples
    - log_entries
    - deployments
    - incidents
    - incident_events
    - incident_evidence
    - feature_flags
    - runbooks

    Filters use exact equality matching.

    Examples:

        query_database(
            entity="payments",
            filters={"status": "FAILED"},
            limit=10
        )

        query_database(
            entity="payment_attempts",
            filters={
                "payment_id": "pay_123"
            },
            limit=10
        )

        query_database(
            entity="deployments",
            filters={
                "service_id": "payment-service"
            },
            limit=10
        )

    IMPORTANT:
    The incidents table intentionally does not expose
    ground_truth_root_cause or resolution because those fields
    are reserved for offline evaluation.
    """

    _validate_entity(entity)
    limit = _validate_limit(limit)

    columns = ENTITY_COLUMNS[entity]

    where_clause, values = _build_filter_clause(
        filters=filters,
        allowed_columns=set(columns),
    )

    selected_columns = ", ".join(
        f'"{column}"'
        for column in columns
    )

    sql = (
        f'SELECT {selected_columns} '
        f'FROM "{entity}"'
        f'{where_clause} '
        f'LIMIT ?'
    )

    values.append(limit)

    connection = _connect()

    try:
        rows = connection.execute(
            sql,
            values,
        ).fetchall()
    except sqlite3.Error as exc:
        raise RuntimeError(
            f"Database query failed for entity "
            f"'{entity}': {exc}"
        ) from exc
    finally:
        connection.close()

    return _format_rows(
        entity=entity,
        columns=columns,
        rows=rows,
    )