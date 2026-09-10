from __future__ import annotations

from typing import TypedDict


class EvidenceItem(TypedDict, total=False):
    source: str
    evidence_type: str
    content: str
    timestamp: str
    service: str
    confidence: float
    metadata: dict


class Hypothesis(TypedDict, total=False):
    hypothesis: str
    confidence: float
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    status: str


class ToolCallRecord(TypedDict, total=False):
    tool_name: str
    input: dict
    output_summary: str
    success: bool


class InvestigationStep(TypedDict, total=False):
    step: int
    action: str
    reason: str
    result: str


class InvestigationState(TypedDict):
    """
    Shared state passed through the LangGraph investigation workflow.
    """

    # Original incident reported by the user.
    incident: str

    # Working investigation context.
    service: str | None
    severity: str | None

    # Evidence collected from tools.
    evidence: list[EvidenceItem]

    # Current competing explanations.
    hypotheses: list[Hypothesis]

    # Audit trail of tool calls.
    tool_calls: list[ToolCallRecord]

    # Human-readable investigation history.
    investigation_steps: list[InvestigationStep]

    # Current investigation status.
    status: str

    # Whether enough evidence exists to stop investigation.
    evidence_sufficient: bool

    # Final outputs.
    root_cause: str | None
    root_cause_confidence: float | None
    recommendations: list[str]