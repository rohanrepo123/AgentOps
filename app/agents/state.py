from __future__ import annotations

from typing import TypedDict


class EvidenceItem(TypedDict, total=False):
    source: str
    evidence_type: str
    content: str
    service: str | None
    timestamp: str | None
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
    incident: str

    service: str | None
    severity: str | None

    evidence: list[EvidenceItem]
    hypotheses: list[Hypothesis]

    tool_calls: list[ToolCallRecord]
    investigation_steps: list[InvestigationStep]

    status: str

    evidence_sufficient: bool

    root_cause: str | None
    root_cause_confidence: float | None

    recommendations: list[str]

    next_action: str | None
    next_action_args: dict
    planner_reason: str | None

    investigation_complete: bool
    max_steps: int