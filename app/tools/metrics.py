from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "acmecloud.db"

ALLOWED_AGGREGATIONS = {
    "avg",
    "min",
    "max",
    "sum",
    "count",
}


@lru_cache(maxsize=1)
def _get_database_path() -> Path:
    """Return the AcmeCloud SQLite database path."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"AcmeCloud database not found at: {DATABASE_PATH}"
        )

    return DATABASE_PATH


def _connect() -> sqlite3.Connection:
    """Open a read-only SQLite connection."""

    database_path = _get_database_path()

    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro",
        uri=True,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    return connection


@tool
def query_metrics(
    metric_name: str,
    service_id: Optional[str] = None,
    environment: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    aggregation: str = "avg",
) -> str:
    """
    Query and aggregate AcmeCloud operational metrics.

    Use this tool to investigate:
    - latency
    - error rates
    - throughput
    - queue depth
    - request volume
    - resource utilization
    - other time-series operational metrics

    The metric_name must match the stored metric name.

    Supported aggregations:
    - avg
    - min
    - max
    - sum
    - count

    Time values should use the same timestamp format stored in
    metric_samples.recorded_at.
    """

    if not metric_name.strip():
        raise ValueError(
            "metric_name cannot be empty."
        )

    aggregation = aggregation.lower()

    if aggregation not in ALLOWED_AGGREGATIONS:
        raise ValueError(
            f"Unsupported aggregation '{aggregation}'. "
            f"Allowed values: {sorted(ALLOWED_AGGREGATIONS)}"
        )

    if start_time and end_time and start_time > end_time:
        raise ValueError(
            "start_time cannot be later than end_time."
        )

    conditions = [
        "metric_name = ?"
    ]

    parameters: list[object] = [
        metric_name
    ]

    if service_id:
        conditions.append(
            "service_id = ?"
        )
        parameters.append(service_id)

    if environment:
        conditions.append(
            "environment = ?"
        )
        parameters.append(environment)

    if start_time:
        conditions.append(
            "recorded_at >= ?"
        )
        parameters.append(start_time)

    if end_time:
        conditions.append(
            "recorded_at <= ?"
        )
        parameters.append(end_time)

    where_clause = " AND ".join(conditions)

    aggregation_sql = {
        "avg": "AVG(metric_value)",
        "min": "MIN(metric_value)",
        "max": "MAX(metric_value)",
        "sum": "SUM(metric_value)",
        "count": "COUNT(*)",
    }[aggregation]

    sql = f"""
        SELECT
            {aggregation_sql} AS aggregated_value,
            COUNT(*) AS sample_count,
            MIN(recorded_at) AS first_recorded_at,
            MAX(recorded_at) AS last_recorded_at
        FROM metric_samples
        WHERE {where_clause}
    """

    connection = _connect()

    try:
        row = connection.execute(
            sql,
            parameters,
        ).fetchone()

    except sqlite3.Error as exc:
        raise RuntimeError(
            f"Metric query failed: {exc}"
        ) from exc

    finally:
        connection.close()

    if row is None or row["sample_count"] == 0:
        return (
            "No metric samples matched the supplied filters."
        )

    return "\n".join(
        [
            f"Metric: {metric_name}",
            f"Service: {service_id or 'all'}",
            f"Environment: {environment or 'all'}",
            f"Aggregation: {aggregation}",
            f"Value: {row['aggregated_value']}",
            f"Sample count: {row['sample_count']}",
            f"First sample: {row['first_recorded_at']}",
            f"Last sample: {row['last_recorded_at']}",
        ]
    )