from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

from langchain_core.tools import tool


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "acmecloud.db"


@lru_cache(maxsize=1)
def _get_database_path() -> Path:
    """Return the AcmeCloud SQLite database path."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"AcmeCloud database not found at: {DATABASE_PATH}"
        )

    return DATABASE_PATH


def _connect() -> sqlite3.Connection:
    """Open the database in read-only mode."""

    database_path = _get_database_path()

    connection = sqlite3.connect(
        f"file:{database_path.as_posix()}?mode=ro",
        uri=True,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    return connection


@tool
def check_service_health(
    service_id: str,
) -> str:
    """
    Inspect the operational health of an AcmeCloud service.

    Returns:
    - current service status
    - service version
    - owner team
    - region
    - dependencies
    - latest deployment
    - enabled feature flags

    Use this tool when investigating:
    - service outages
    - degraded services
    - dependency failures
    - recent deployments
    - feature-flag related incidents
    """

    if not service_id.strip():
        raise ValueError(
            "service_id cannot be empty."
        )

    connection = _connect()

    try:
        # -------------------------------------------------------------
        # Service
        # -------------------------------------------------------------

        service = connection.execute(
            """
            SELECT
                service_id,
                service_name,
                description,
                owner_team,
                version,
                status,
                region
            FROM services
            WHERE service_id = ?
            """,
            (service_id,),
        ).fetchone()

        if service is None:
            return (
                f"Service '{service_id}' was not found."
            )

        # -------------------------------------------------------------
        # Dependencies
        # -------------------------------------------------------------

        dependencies = connection.execute(
            """
            SELECT
                source_service,
                target_service,
                dependency_type,
                criticality,
                timeout_ms
            FROM service_dependencies
            WHERE source_service = ?
            ORDER BY criticality DESC
            """,
            (service_id,),
        ).fetchall()

        # -------------------------------------------------------------
        # Latest deployment
        # -------------------------------------------------------------

        deployment = connection.execute(
            """
            SELECT
                deployment_id,
                version,
                previous_version,
                environment,
                deployed_by,
                status,
                change_summary,
                deployed_at
            FROM deployments
            WHERE service_id = ?
            ORDER BY deployed_at DESC
            LIMIT 1
            """,
            (service_id,),
        ).fetchone()

        # -------------------------------------------------------------
        # Feature flags
        # -------------------------------------------------------------

        feature_flags = connection.execute(
            """
            SELECT
                flag_id,
                flag_name,
                enabled,
                rollout_percentage,
                updated_at
            FROM feature_flags
            WHERE service_id = ?
            ORDER BY flag_name
            """,
            (service_id,),
        ).fetchall()

    except sqlite3.Error as exc:
        raise RuntimeError(
            f"Service health query failed: {exc}"
        ) from exc

    finally:
        connection.close()

    # ---------------------------------------------------------------
    # Format output
    # ---------------------------------------------------------------

    output = [
        "SERVICE HEALTH",
        f"Service ID: {service['service_id']}",
        f"Service Name: {service['service_name']}",
        f"Status: {service['status']}",
        f"Version: {service['version']}",
        f"Owner Team: {service['owner_team']}",
        f"Region: {service['region']}",
        "",
    ]

    # Dependencies
    output.append(
        f"DEPENDENCIES ({len(dependencies)})"
    )

    if dependencies:
        for dependency in dependencies:
            output.append(
                " - "
                f"{dependency['target_service']} | "
                f"type={dependency['dependency_type']} | "
                f"criticality={dependency['criticality']} | "
                f"timeout={dependency['timeout_ms']}ms"
            )
    else:
        output.append(" - None")

    output.append("")

    # Latest deployment
    output.append("LATEST DEPLOYMENT")

    if deployment:
        output.extend(
            [
                f" - Deployment ID: {deployment['deployment_id']}",
                f" - Version: {deployment['version']}",
                f" - Previous Version: {deployment['previous_version']}",
                f" - Environment: {deployment['environment']}",
                f" - Status: {deployment['status']}",
                f" - Deployed By: {deployment['deployed_by']}",
                f" - Deployed At: {deployment['deployed_at']}",
                f" - Change: {deployment['change_summary']}",
            ]
        )
    else:
        output.append(" - No deployment record found.")

    output.append("")

    # Feature flags
    output.append(
        f"FEATURE FLAGS ({len(feature_flags)})"
    )

    if feature_flags:
        for flag in feature_flags:
            output.append(
                " - "
                f"{flag['flag_name']} | "
                f"enabled={bool(flag['enabled'])} | "
                f"rollout={flag['rollout_percentage']}% | "
                f"updated={flag['updated_at']}"
            )
    else:
        output.append(" - None")

    return "\n".join(output)