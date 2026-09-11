from __future__ import annotations

import os

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.agents.state import InvestigationState


ALLOWED_ACTIONS = {
    "check_service_health",
    "search_logs",
    "query_metrics",
    "query_database",
    "search_documentation",
    "finish",
}


class PlannerDecision(BaseModel):
    """Structured decision produced by the investigation planner."""

    action: str = Field(
        description=(
            "The next investigation action. "
            "Must be one of the allowed tool names or finish."
        )
    )

    reason: str = Field(
        description=(
            "Why this action is the most useful next step "
            "given the current evidence."
        )
    )


# def _get_planner_model() -> ChatOpenAI:
def _get_planner_model() -> ChatOllama:
    """
    Create the LLM used by the investigation planner.

    The model is configurable through AGENTOPS_PLANNER_MODEL.
    """

    model_name = os.getenv(
        "AGENTOPS_PLANNER_MODEL",
        # "gpt-4.1-mini",
        "nemotron-3-super:cloud",
    )

    return ChatOllama(
        model=model_name,
        temperature=0,
    )


def _format_evidence(
    state: InvestigationState,
) -> str:
    """
    Create a compact planner context from collected evidence.

    We deliberately truncate individual evidence items so that
    operational logs and database records do not consume the
    planner's entire context window.
    """

    evidence = state.get("evidence", [])

    if not evidence:
        return "No evidence has been collected yet."

    sections: list[str] = []

    for index, item in enumerate(evidence, start=1):

        content = item.get("content", "")

        if len(content) > 2500:
            content = content[:2500] + "\n...[truncated]"

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


def _build_prompt(
    state: InvestigationState,
) -> str:
    """Build the planner prompt."""

    incident = state["incident"]
    service = state.get("service")
    severity = state.get("severity")

    evidence_context = _format_evidence(state)

    available_actions = ", ".join(
        sorted(ALLOWED_ACTIONS)
    )

    return f"""
You are the investigation planner for AgentOps.

Your job is to decide the SINGLE most useful next investigation
action for the current production incident.

Incident:
{incident}

Affected service:
{service or "unknown"}

Severity:
{severity or "unknown"}

Available actions:
{available_actions}

Current evidence:
{evidence_context}

Investigation rules:

1. Prefer actions that gather NEW information.
2. Do not repeatedly call the same tool unless the existing
   evidence indicates a more targeted second investigation
   would be useful.
3. Correlate evidence across services, logs, metrics,
   deployments, database state, and documentation.
4. Do not assume a root cause without supporting evidence.
5. Choose "finish" only when the evidence is sufficient
   to support a plausible root-cause analysis.
6. Never expose or request evaluation-only ground-truth fields.
7. Return exactly one next action.
"""


def plan_next_action(
    state: InvestigationState,
) -> PlannerDecision:
    """
    Ask the LLM planner which investigation action should
    happen next.
    """

    model = _get_planner_model().with_structured_output(
        PlannerDecision
    )

    response = model.invoke(
        _build_prompt(state)
    )

    if response.action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Planner returned unsupported action: "
            f"{response.action}"
        )

    return response