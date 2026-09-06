from typing import Optional

from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """
    Represents one retrieved document chunk.
    """

    content: str = Field(
        ...,
        description="Text content of the retrieved chunk.",
    )

    score: float = Field(
        ...,
        description="Retrieval relevance score.",
    )

    document_id: str = Field(
        ...,
        description="Unique identifier of the source document.",
    )

    source: str = Field(
        ...,
        description="Relative path or source identifier.",
    )

    category: str = Field(
        ...,
        description="Document category such as service, runbook, etc.",
    )

    document_type: str = Field(
        ...,
        description="Type of document.",
    )

    service: Optional[str] = Field(
        default=None,
        description="Associated AcmeCloud service.",
    )

    chunk_id: Optional[str] = Field(
        default=None,
        description="Unique chunk identifier.",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Additional source metadata.",
    )


class RetrievalResponse(BaseModel):
    """
    Complete response returned by the retrieval pipeline.
    """

    query: str

    results: list[RetrievalResult] = Field(
        default_factory=list
    )

    total_results: int = 0

    retrieval_time_ms: float = 0.0