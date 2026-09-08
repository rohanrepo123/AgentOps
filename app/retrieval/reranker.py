from __future__ import annotations

from typing import Sequence

from sentence_transformers import CrossEncoder

from app.retrieval.config import retrieval_config
from app.retrieval.schemas import RetrievalResult

class DocumentReranker:
    """Rerank retrieval candidates with a local cross-encoder."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or retrieval_config.reranker_model
        self.model = CrossEncoder(
            self.model_name,
            max_length=retrieval_config.reranker_max_length,
        )

    def rerank(
        self,
        query: str,
        candidates: Sequence[RetrievalResult],
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than 0.")
        if not candidates:
            return []

        pairs = [(query, candidate.content) for candidate in candidates]
        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
            batch_size=retrieval_config.reranker_batch_size,
        )

        reranked = [
            candidate.model_copy(
                update={"reranker_score": float(score)}
            )
            for candidate, score in zip(candidates, scores)
        ]

        reranked.sort(
            key=lambda item: (
                item.reranker_score
                if item.reranker_score is not None
                else float("-inf")
            ),
            reverse=True,
        )
        if top_k is not None:
            return reranked[:top_k]
        
        return reranked
