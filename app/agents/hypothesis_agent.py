from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama


class HypothesisUpdate(BaseModel):
    hypothesis: str = Field(
        description="Potential root cause"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the hypothesis"
    )

    supporting_evidence: list[str] = Field(
        default_factory=list
    )

    contradicting_evidence: list[str] = Field(
        default_factory=list
    )

    status: str = Field(
        description="supported, plausible, weakened, or rejected"
    )


class HypothesisAnalysis(BaseModel):
    hypotheses: list[HypothesisUpdate]

MODEL_NAME = "nemotron-3-super:cloud"


def analyze_hypotheses(state) -> HypothesisAnalysis:

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
    )

    structured_llm = llm.with_structured_output(
        HypothesisAnalysis
    )

    evidence_text = "\n\n".join(
        f"""
Evidence {i + 1}
Type: {item.get("evidence_type")}
Source: {item.get("source")}
Content:
{item.get("content", "")[:2500]}
"""
        for i, item in enumerate(
            state.get("evidence", [])
        )
    )

    prompt = f"""
You are the hypothesis analysis agent for a
production incident investigation system.

Incident:
{state.get("incident")}

Affected service:
{state.get("service")}

Severity:
{state.get("severity")}

Existing hypotheses:
{state.get("hypotheses", [])}

New evidence:
{evidence_text}

Evaluate the existing hypotheses against the evidence.

You may:
1. strengthen a hypothesis
2. weaken a hypothesis
3. reject a hypothesis
4. introduce a new hypothesis if strongly justified

Do not claim a root cause without evidence.

Confidence must reflect the strength of the available evidence.

Possible statuses:
- supported
- plausible
- weakened
- rejected

Return structured hypothesis updates.
"""

    return structured_llm.invoke(prompt)