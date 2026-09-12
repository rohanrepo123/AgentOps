from __future__ import annotations

import json
import os
from typing import Any

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from app.agents.state import InvestigationState


ALLOWED_ACTIONS = {
    "check_service_health",
    "search_logs",
    "query_metrics",
    "query_database",
    "find_duplicate_payments",
    "payment_attempt_history",
    "recent_deployments",
    "search_documentation",
    "finish",
}

class PlannerDecision(BaseModel):
    """Structured decision produced by the investigation planner."""

    action: str = Field(
        description=(
            "The single next investigation action. "
            "Must be one of the allowed action names."
        )
    )

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Arguments required by the selected action. "
            "Use only arguments supported by that action."
        ),
    )

    reason: str = Field(
        description=(
            "Why this action and these arguments are the "
            "most useful next investigation step."
        )
    )


def _get_planner_model() -> ChatOpenRouter:
# def _get_planner_model() -> ChatOpenAI:
# def _get_planner_model() -> ChatOllama:
    """
    Create the LLM used by the investigation planner.

    The model is configurable through AGENTOPS_PLANNER_MODEL.
    """

    model_name = os.getenv(
        "AGENTOPS_PLANNER_MODEL",
        # "gpt-4.1-mini",
        # "nemotron-3-super:cloud",
        # "inclusionai/ling-3.0-flash-fin:free",
        "nvidia/nemotron-3.5-lightning:free",
    )

    return ChatOpenRouter(
        model=model_name,
        temperature=0,
    )


def _format_evidence(
    state: InvestigationState,
) -> str:
    """Format collected evidence into compact planner context."""

    evidence = state.get("evidence", [])

    if not evidence:
        return "No evidence has been collected yet."

    sections: list[str] = []

    for index, item in enumerate(evidence, start=1):

        content = item.get("content", "")

        if len(content) > 2500:
            content = (
                content[:2500]
                + "\n...[truncated]"
            )

        sections.append(
            "\n".join(
                [
                    f"[Evidence {index}]",
                    f"Type: {item.get('evidence_type')}",
                    f"Source: {item.get('source')}",
                    f"Service: {item.get('service')}",
                    content,
                ]
            )
        )

    return "\n\n".join(sections)


def _format_previous_actions(
    state: InvestigationState,
) -> str:
    """Show previous tool calls and their outcomes."""

    tool_calls = state.get("tool_calls", [])

    if not tool_calls:
        return "No tools have been called yet."
    
    lines: list[str] = []

    for call in tool_calls:
        lines.append(
            json.dumps(
                {
                    "tool": call.get("tool_name"),
                    "input": call.get("input"),
                    "success": call.get("success"),
                    "result": call.get("output_summary"),
                },
                default=str,
            )
        )


    return "\n".join(lines)


def _build_prompt(
    state: InvestigationState,
) -> str:
    """Build the planner prompt."""

    incident = state["incident"]
    service = state.get("service")
    severity = state.get("severity")

    evidence_context = _format_evidence(state)
    previous_actions = _format_previous_actions(state)
    hypotheses_text = "\n".join(
        f"""
    Hypothesis: {h.get('hypothesis')}
    Confidence: {h.get('confidence')}
    Status: {h.get('status')}
    Supporting evidence: {h.get('supporting_evidence')}
    Contradicting evidence: {h.get('contradicting_evidence')}
    """
        for h in state.get("hypotheses", [])
    )

    return f"""

You are the investigation planner for AgentOps.

Your task is to choose the SINGLE most useful next investigation
action and provide the exact arguments required for that action.

INCIDENT
{incident}

AFFECTED SERVICE
{service or "unknown"}

SEVERITY
{severity or "unknown"}


CURRENT HYPOTHESES
------------------
{hypotheses_text}

ALLOWED ACTIONS
- check_service_health
- search_logs
- query_metrics
- query_database
- search_documentation
- finish

AVAILABLE ARGUMENT SCHEMAS

1. check_service_health
{{
  "service_id": "<service id>"
}}

2. search_logs
{{
  "query": "<keyword or phrase>",
  "service_id": "<optional service id>",
  "level": "<optional DEBUG|INFO|WARN|ERROR|CRITICAL>",
  "event_type": "<optional event type>",
  "start_time": "<optional timestamp>",
  "end_time": "<optional timestamp>",
  "trace_id": "<optional trace id>",
  "request_id": "<optional request id>",
  "user_id": "<optional user id>",
  "limit": <optional integer <= 100>
}}

3. query_metrics

Allowed metric names:
- cpu_usage
- error_rate
- memory_usage
- p95_latency_ms
- queue_depth
- request_rate
- retry_rate

Arguments:
{{
  "metric_name": "<allowed metric>",
  "service_id": "<optional service id>",
  "environment": "<optional environment>",
  "start_time": "<optional timestamp>",
  "end_time": "<optional timestamp>",
  "aggregation": "<avg|min|max|sum|count>"
}}

4. query_database

Allowed entities and their filterable columns:

- services
  columns:
  service_id, service_name, owner_team, version, status, region

- service_dependencies
  columns:
  dependency_id, source_service, target_service,
  dependency_type, criticality, timeout_ms

- users
  columns:
  user_id, email, plan, country, account_status, created_at

- subscriptions
  columns:
  subscription_id, user_id, plan, status, started_at, cancelled_at

- payments
  columns:
  payment_id, user_id, subscription_id, transaction_id,
  amount, currency, provider, status, idempotency_key, created_at

- payment_attempts
  columns:
  attempt_id, payment_id, attempt_number,
  provider_request_id, result, latency_ms,
  error_code, created_at

- api_requests
  columns:
  request_id, service_id, user_id, method, endpoint,
  status_code, latency_ms, trace_id, created_at

- metric_samples
  columns:
  sample_id, service_id, metric_name, metric_value,
  unit, environment, recorded_at

- log_entries
  columns:
  log_id, timestamp, service_id, level, event_type,
  trace_id, request_id, user_id

- deployments
  columns:
  deployment_id, service_id, version, previous_version,
  environment, deployed_by, status, deployed_at

- incidents
  columns:
  incident_id, title, description, severity,
  status, affected_service, start_time, resolved_time

- incident_events
  columns:
  event_id, incident_id, event_time, event_type, source

- incident_evidence
  columns:
  evidence_id, incident_id, evidence_type,
  reference_id, relevance

- feature_flags
  columns:
  flag_id, flag_name, service_id, enabled,
  rollout_percentage, updated_at

- runbooks
  columns:
  runbook_id, title, service_id,
  trigger_condition, last_updated

Important database rules:
- Only use filter columns belonging to the selected entity.
- Never invent a column.
- Filters currently support EXACT equality only.
- Do NOT use operators such as $gte, $lte, $gt, $lt, $in, or $ne.
- Do not use service_id for payment_attempts.
- For service-specific payment investigation:
  query payments or use payment_id to inspect payment_attempts.
- Never expose incidents.ground_truth_root_cause or incidents.resolution.

5. find_duplicate_payments

{
  "service_id": "<service id>",
  "limit": <optional integer <= 100>
}

Use this action when investigating possible duplicate
payment transactions.

6. payment_attempt_history

{
  "payment_id": "<payment id>",
  "limit": <optional integer <= 100>
}

Use this action when investigating retries, timeouts,
or multiple attempts for a specific payment.

7. recent_deployments

{
  "service_id": "<service id>",
  "limit": <optional integer <= 50>
}

Use this action when investigating whether a recent
deployment may have contributed to the incident.


8. search_documentation
{{
  "query": "<investigation query>",
  "service": "<optional service id>"
}}

9. finish
Use:
{{
  "arguments": {{}}
}}

CURRENT EVIDENCE
{evidence_context}

PREVIOUS TOOL CALLS
{previous_actions}

INVESTIGATION RULES

1. Choose the action that gives the highest information value.
2. Prefer NEW evidence over repeating an already successful query.
3. Use previous evidence to refine the next query.
4. Correlate multiple signal types instead of relying on one source.
5. When evidence points to a specific service, inspect that service.
6. For payment incidents, payment attempts, retry rate, logs,
   idempotency configuration, and deployments may be especially relevant.
7. For latency incidents, inspect p95 latency, error rate,
   dependencies, logs, and recent deployments.
8. Do not invent database columns.
9. Do not request unrestricted SQL.
10. Never request or expose evaluation-only ground-truth fields.
11. Choose "finish" only when the collected evidence is sufficient
    to support a defensible root-cause analysis.
12. Return exactly one action.
13. Arguments must match the selected action's schema.

Filters currently support exact equality only.

Valid:
{{"status": "FAILED"}}

Invalid:
{{"created_at": {{"$gte": "2026-09-01T00:00:00"}}}}

Do not use:
$gte
$lte
$gt
$lt
$in
$ne


Your next action must be selected based on the
current hypotheses and the evidence gap.

Do not repeat an investigation action unless:
- it is required to validate a hypothesis, or
- previous evidence was insufficient.
"""


def _validate_arguments(
    decision: PlannerDecision,
) -> None:
    """Validate planner arguments before the graph executes them."""

    action = decision.action
    arguments = decision.arguments

    if action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Planner returned unsupported action: {action}"
        )

    if not isinstance(arguments, dict):
        raise ValueError(
            "Planner arguments must be a dictionary."
        )

    required_fields = {
        "check_service_health": {"service_id"},
        "search_logs": set(),
        "query_metrics": {"metric_name"},
        "query_database": {"entity"},
        "find_duplicate_payments": set(),
        "payment_attempt_history": {"payment_id"},
        "recent_deployments": {"service_id"},
        "search_documentation": {"query"},
        "finish": set(),
    }

    missing = (
        required_fields[action]
        - set(arguments.keys())
    )

    if missing:
        raise ValueError(
            f"Planner action '{action}' is missing "
            f"required arguments: {sorted(missing)}"
        )

    if action == "query_metrics":

        allowed_metrics = {
            "cpu_usage",
            "error_rate",
            "memory_usage",
            "p95_latency_ms",
            "queue_depth",
            "request_rate",
            "retry_rate",
        }

        metric_name = arguments.get(
            "metric_name"
        )

        if metric_name not in allowed_metrics:
            raise ValueError(
                f"Unsupported metric_name: {metric_name}"
            )

    if action == "query_database":

        allowed_entities = {
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

        entity = arguments.get("entity")

        if entity not in allowed_entities:
            raise ValueError(
                f"Unsupported database entity: {entity}"
            )


def plan_next_action(
    state: InvestigationState,
) -> PlannerDecision:
    """Ask the LLM which tool to execute next."""

    model = _get_planner_model().with_structured_output(
        PlannerDecision
    )

    response = model.invoke(
        _build_prompt(state)
    )

    if response is None:
        raise RuntimeError(
            "Planner model returned no structured decision."
        )

    _validate_arguments(response)

    return response
