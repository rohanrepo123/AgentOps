from typing import Optional

from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """Represents one retrieved document chunk."""

    content: str = Field(..., description="Text content of the retrieved chunk.")
    score: float = Field(..., description="Original FAISS retrieval score.")
    reranker_score: Optional[float] = Field(
        default=None,
        description="Cross-encoder reranker score, when reranking is enabled.",
    )
    document_id: str = Field(..., description="Unique source document identifier.")
    source: str = Field(..., description="Relative path or source identifier.")
    category: str = Field(..., description="Document category.")
    document_type: str = Field(..., description="Document type.")
    service: Optional[str] = Field(default=None, description="Associated service.")
    chunk_id: Optional[str] = Field(default=None, description="Unique chunk ID.")
    metadata: dict = Field(default_factory=dict)


class RetrievalResponse(BaseModel):
    """Complete response returned by the retrieval pipeline."""

    query: str

    retrieval_queries: list[str] = Field(
        default_factory=list,
        description="Queries used for candidate retrieval.",
    )

    raw_candidate_count: int = Field(
        default=0,
        description=(
            "Total number of candidates returned by FAISS "
            "across all retrieval queries before deduplication."
        ),
    )

    candidate_pool_size: int = Field(
        default=0,
        description=(
            "Number of unique retrieved chunks after "
            "merging and deduplication."
        ),
    )

    unique_candidate_documents: int = Field(
        default=0,
        description=(
            "Number of unique source documents represented "
            "in the candidate pool."
        ),
    )

    results: list[RetrievalResult] = Field(
        default_factory=list
    )

    total_results: int = 0
    retrieval_time_ms: float = 0.0