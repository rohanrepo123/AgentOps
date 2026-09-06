from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class RetrievalEvaluationCase(BaseModel):
    """
    One retrieval evaluation example.
    """

    query_id: str

    query: str

    service: str | None = None

    relevant_documents: list[str] = Field(
        default_factory=list
    )


def load_retrieval_dataset(
    path: Path,
) -> list[RetrievalEvaluationCase]:
    """
    Load retrieval benchmark cases from JSON.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError(
            "Retrieval dataset must contain a JSON list."
        )

    cases = [
        RetrievalEvaluationCase.model_validate(
            item
        )
        for item in raw_data
    ]

    if not cases:
        raise ValueError(
            "Retrieval evaluation dataset is empty."
        )

    return cases