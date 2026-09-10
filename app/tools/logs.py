from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "acmecloud.db"


# ---------------------------------------------------------------------
# Allowed log levels
# ---------------------------------------------------------------------

ALLOWED_LEVELS = {
    "DEBUG",
    "INFO",
    "WARN",
    "ERROR",
    "CRITICAL",
}


# ---------------------------------------------------------------------
# Database
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
    """Open the SQLite database in read-only mode."""

    database_path = _get_database_path()

    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro",
        uri=True,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------

@tool
def search_logs(
    query: Optional[str] = None,
    service_id: Optional[str] = None,
    level: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    Search AcmeCloud operational logs.

    Use this tool to investigate:
    - errors and exceptions
    - retries and timeouts
    - authentication failures
    - queue failures
    - API failures
    - suspicious events
    - request-level problems

    Search behavior:
    - query performs case-insensitive keyword matching against
      message and event_type.
    - service_id filters logs for one service.
    - level filters by log severity.
    - event_type filters by exact event type.
    - start_time and end_time define an optional time window.
    - trace_id, request_id, and user_id allow correlation.
    - results are returned newest first.

    The tool is read-only and does not allow arbitrary SQL.
    """

    # ---------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------

    if limit <= 0:
        raise ValueError(
            "limit must be greater than 0."
        )

    limit = min(limit, 100)

    if level is not None:
        level = level.upper()

        if level not in ALLOWED_LEVELS:
            raise ValueError(
                f"Invalid log level '{level}'. "
                f"Allowed levels: {sorted(ALLOWED_LEVELS)}"
            )

    if start_time and end_time and start_time > end_time:
        raise ValueError(
            "start_time cannot be later than end_time."
        )

    # ---------------------------------------------------------------
    # Build parameterized query
    # ---------------------------------------------------------------

    conditions: list[str] = []
    parameters: list[object] = []

    if query and query.strip():

        search_term = query.strip()

        conditions.append(
            """
            (
                LOWER(message) LIKE LOWER(?)
                OR LOWER(event_type) LIKE LOWER(?)
            )
            """
        )

        wildcard = f"%{search_term}%"

        parameters.extend(
            [
                wildcard,
                wildcard,
            ]
        )

    if service_id:
        conditions.append(
            "service_id = ?"
        )
        parameters.append(service_id)

    if level:
        conditions.append(
            "level = ?"
        )
        parameters.append(level)

    if event_type:
        conditions.append(
            "event_type = ?"
        )
        parameters.append(event_type)

    if start_time:
        conditions.append(
            "timestamp >= ?"
        )
        parameters.append(start_time)

    if end_time:
        conditions.append(
            "timestamp <= ?"
        )
        parameters.append(end_time)

    if trace_id:
        conditions.append(
            "trace_id = ?"
        )
        parameters.append(trace_id)

    if request_id:
        conditions.append(
            "request_id = ?"
        )
        parameters.append(request_id)

    if user_id:
        conditions.append(
            "user_id = ?"
        )
        parameters.append(user_id)

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    sql = f"""
        SELECT
            log_id,
            timestamp,
            service_id,
            level,
            event_type,
            message,
            trace_id,
            request_id,
            user_id,
            metadata_json
        FROM log_entries
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ?
    """

    parameters.append(limit)

    # ---------------------------------------------------------------
    # Execute
    # ---------------------------------------------------------------

    connection = _connect()

    try:
        rows = connection.execute(
            sql,
            parameters,
        ).fetchall()

    except sqlite3.Error as exc:

        raise RuntimeError(
            f"Log search failed: {exc}"
        ) from exc

    finally:
        connection.close()

    # ---------------------------------------------------------------
    # Format result
    # ---------------------------------------------------------------

    if not rows:
        return (
            "No log entries matched the supplied filters."
        )

    output = [
        f"Log entries returned: {len(rows)}",
        "",
    ]

    for index, row in enumerate(rows, start=1):

        output.extend(
            [
                f"[Log {index}]",
                f"log_id: {row['log_id']}",
                f"timestamp: {row['timestamp']}",
                f"service_id: {row['service_id']}",
                f"level: {row['level']}",
                f"event_type: {row['event_type']}",
                f"message: {row['message']}",
                f"trace_id: {row['trace_id']}",
                f"request_id: {row['request_id']}",
                f"user_id: {row['user_id']}",
                f"metadata_json: {row['metadata_json']}",
                "",
            ]
        )

    return "\n".join(output)