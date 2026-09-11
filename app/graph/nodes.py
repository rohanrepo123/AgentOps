from __future__ import annotations

from typing import Any
from app.agents.planner import plan_next_action
from app.agents.state import InvestigationState
from app.tools.database import query_database
from app.tools.documentation import search_documentation
from app.tools.logs import search_logs
from app.tools.metrics import query_metrics
from app.tools.service_health import check_service_health


def _append_evidence(
    state: InvestigationState,
    *,
    source: str,
    evidence_type: str,
    content: str,
    service: str | None = None,
    timestamp: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> list[dict]:
    """Append one evidence item to the existing evidence list."""

    evidence = list(state.get("evidence", []))

    evidence.append(
        {
            "source": source,
            "evidence_type": evidence_type,
            "content": content,
            "service": service,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }
    )

    return evidence


def _append_tool_call(
    state: InvestigationState,
    *,
    tool_name: str,
    tool_input: dict,
    output: str,
    success: bool = True,
) -> list[dict]:
    """Append an audit record for one tool invocation."""

    tool_calls = list(state.get("tool_calls", []))

    tool_calls.append(
        {
            "tool_name": tool_name,
            "input": tool_input,
            "output_summary": output[:1000],
            "success": success,
            
        }
    )

    return tool_calls


def _append_step(
    state: InvestigationState,
    *,
    action: str,
    reason: str,
    result: str,
) -> list[dict]:
    """Append one investigation step."""

    steps = list(state.get("investigation_steps", []))

    steps.append(
        {
            "step": len(steps) + 1,
            "action": action,
            "reason": reason,
            "result": result[:1000],
        }
    )

    return steps


# ---------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------

def service_health_node(
    state: InvestigationState,
) -> InvestigationState:
    """Inspect the affected service and its operational dependencies."""

    service = state.get("service")

    if not service:
        raise ValueError(
            "Investigation state must contain a service."
        )

    tool_input = dict(
        state.get(
            "next_action_args",
            {},
        )
    )

    if "service_id" not in tool_input:
        tool_input["service_id"] = service

        try:
            output = check_service_health.invoke(tool_input)
            success = True
        except Exception as exc:
            output = f"Service health lookup failed: {exc}"
            success = False

    return {
        **state,
        "evidence": _append_evidence(
            state,
            source="check_service_health",
            evidence_type="service_health",
            content=output,
            service=service,
        ),
        "tool_calls": _append_tool_call(
            state,
            tool_name="check_service_health",
            tool_input=tool_input,
            output=output,
            success=success,
        ),
        "investigation_steps": _append_step(
            state,
            action="check_service_health",
            reason="Establish baseline health, dependencies, deployment, and feature-flag state.",
            result=output,
        ),
    }


def logs_node(
    state: InvestigationState,
) -> InvestigationState:
    """Search operational logs related to the incident."""

    service = state.get("service")
    incident = state["incident"]

    tool_input = dict(
        state.get(
            "next_action_args",
            {},
        )
    )

    tool_input.setdefault(
        "service_id",
        service,
    )

    tool_input.setdefault(
        "limit",
        20,
    )

    try:
        output = search_logs.invoke(tool_input)
        success = True
    except Exception as exc:
        output = f"Log search failed: {exc}"
        success = False

    return {
        **state,
        "evidence": _append_evidence(
            state,
            source="search_logs",
            evidence_type="logs",
            content=output,
            service=service,
        ),
        "tool_calls": _append_tool_call(
            state,
            tool_name="search_logs",
            tool_input=tool_input,
            output=output,
            success=success,
        ),
        "investigation_steps": _append_step(
            state,
            action="search_logs",
            reason="Look for operational failures related to the incident.",
            result=output,
        ),
    }


def metrics_node(
    state: InvestigationState,
) -> InvestigationState:
    """Inspect the service's p95 latency during investigation."""

    service = state.get("service")

    tool_input = dict(
        state.get(
            "next_action_args",
            {},
        )
    )

    tool_input.setdefault(
        "service_id",
        service,
    )

    tool_input.setdefault(
        "environment",
        "production",
    )

    tool_input.setdefault(
        "aggregation",
        "avg",
    )

    try:
        output = query_metrics.invoke(tool_input)
        success = True
    except Exception as exc:
        output = f"Metric query failed: {exc}"
        success = False

    return {
        **state,
        "evidence": _append_evidence(
            state,
            source="query_metrics",
            evidence_type="metrics",
            content=output,
            service=service,
        ),
        "tool_calls": _append_tool_call(
            state,
            tool_name="query_metrics",
            tool_input=tool_input,
            output=output,
            success=success,
        ),
        "investigation_steps": _append_step(
            state,
            action="query_metrics",
            reason="Establish an aggregate latency signal for the affected service.",
            result=output,
        ),
    }


def database_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Run a controlled database probe.

    The first version uses the incident text to select a
    relevant operational entity. This will later be replaced
    by the adaptive planner.
    """

    # incident = state["incident"]
    # incident_lower = incident.lower()

    # if "payment" in incident_lower or "charge" in incident_lower:
    #     entity = "payments"

    # elif "subscription" in incident_lower or "upgrade" in incident_lower:
    #     entity = "subscriptions"

    # elif "user" in incident_lower or "account" in incident_lower:
    #     entity = "users"

    # elif "deployment" in incident_lower or "release" in incident_lower:
    #     entity = "deployments"

    # else:
    #     entity = "api_requests"

    # tool_input = {
    #     "entity": entity,
    #     "limit": 20,
    # }
    print(
    "\n[DEBUG] database_node next_action_args:",
    state.get("next_action_args"),
)
    tool_input = dict(
    state.get(
        "next_action_args",
        {},
        )
    )

    tool_input.setdefault(
        "limit",
        20,
    )
    try:
        output = query_database.invoke(tool_input)
        success = True
    except Exception as exc:
        output = f"Database query failed: {exc}"
        success = False

    return {
        **state,
        "evidence": _append_evidence(
            state,
            source="query_database",
            evidence_type="database",
            content=output,
        ),
        "tool_calls": _append_tool_call(
            state,
            tool_name="query_database",
            tool_input=tool_input,
            output=output,
            success=success,
        ),
        "investigation_steps": _append_step(
            state,
            action="query_database",
            reason=(
                f"Inspect operational entity "
                f"'{tool_input.get('entity', 'unknown')}' "
                "using planner-selected filters."
            ),
            result=output,
        ),
    }


def documentation_node(
    state: InvestigationState,
) -> InvestigationState:
    """Search engineering documentation for relevant guidance."""

    incident = state["incident"]
    service = state.get("service")

    tool_input = dict(
        state.get(
            "next_action_args",
            {},
        )
    )

    tool_input.setdefault(
        "query",
        state["incident"],
    )

    tool_input.setdefault(
        "service",
        service,
    )

    try:
        output = search_documentation.invoke(tool_input)
        success = True
    except Exception as exc:
        output = f"Documentation search failed: {exc}"
        success = False

    return {
        **state,
        "evidence": _append_evidence(
            state,
            source="search_documentation",
            evidence_type="documentation",
            content=output,
            service=service,
        ),
        "tool_calls": _append_tool_call(
            state,
            tool_name="search_documentation",
            tool_input=tool_input,
            output=output,
            success=success,
        ),
        "investigation_steps": _append_step(
            state,
            action="search_documentation",
            reason="Retrieve engineering documentation and troubleshooting guidance.",
            result=output,
        ),
    }


def finalize_node(
    state: InvestigationState,
) -> InvestigationState:
    """Mark the deterministic investigation pass as complete."""

    return {
        **state,
        "status": "evidence_collected",
        "evidence_sufficient": True,
    }

def planner_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Decide the next investigation action using the LLM planner.
    """

    steps = state.get(
        "investigation_steps",
        [],
    )

    max_steps = state.get(
        "max_steps",
        8,
    )

    if len(steps) >= max_steps:
        return {
            **state,
            "next_action": "finish",
            "next_action_args": state.get(
            "next_action_args",
            {}
        ),
            "planner_reason": (
                "Maximum investigation step limit reached."
            ),
        }

    decision = plan_next_action(state)

    return {
        **state,
        "next_action": decision.action,
        "next_action_args": state.get(
            "next_action_args",
            {}
        ),
        "planner_reason": decision.reason,
        "investigation_steps": _append_step(
            state,
            action="planner",
            reason=decision.reason,
            result=(
                f"{decision.action} "
                f"{decision.arguments}"
            ),
        ),
    }

def route_next_action(
    state: InvestigationState,
) -> str:
    """
    Route the graph based on the planner's decision.
    """

    action = state.get("next_action")

    if action not in {
        "check_service_health",
        "search_logs",
        "query_metrics",
        "query_database",
        "search_documentation",
        "finish",
    }:
        raise ValueError(
            f"Invalid next action: {action}"
        )

    return action