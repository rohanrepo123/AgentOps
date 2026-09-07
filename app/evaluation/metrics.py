from __future__ import annotations

from typing import Iterable


def unique_document_ids(
    retrieved_documents: Iterable[str],
) -> list[str]:
    """
    Remove duplicate document IDs while preserving order.
    """

    seen: set[str] = set()
    unique: list[str] = []

    for document_id in retrieved_documents:

        if document_id in seen:
            continue

        seen.add(document_id)
        unique.append(document_id)

    return unique


def recall_at_k(
    retrieved_documents: list[str],
    relevant_documents: list[str],
    k: int,
) -> float:
    """
    Recall@K:

        relevant retrieved documents / total relevant documents
    """

    if not relevant_documents:
        return 0.0

    retrieved = set(
        unique_document_ids(
            retrieved_documents[:k]
        )
    )

    relevant = set(
        relevant_documents
    )

    return len(
        retrieved & relevant
    ) / len(relevant)


def precision_at_k(
    retrieved_documents: list[str],
    relevant_documents: list[str],
    k: int,
) -> float:
    """
    Precision@K:

        relevant retrieved documents / K

    Only unique documents are considered.
    """

    unique_retrieved = unique_document_ids(
        retrieved_documents
    )[:k]

    if not unique_retrieved:
        return 0.0

    relevant = set(
        relevant_documents
    )

    relevant_count = sum(
        1
        for document_id
        in unique_retrieved
        if document_id in relevant
    )

    return (
        relevant_count
        / len(unique_retrieved)
    )


def hit_rate_at_k(
    retrieved_documents: list[str],
    relevant_documents: list[str],
    k: int,
) -> float:
    """
    Returns 1 if at least one relevant document
    appears in the top-K results, otherwise 0.
    """

    retrieved = set(
        unique_document_ids(
            retrieved_documents[:k]
        )
    )

    relevant = set(
        relevant_documents
    )

    return (
        1.0
        if retrieved & relevant
        else 0.0
    )


def reciprocal_rank(
    retrieved_documents: list[str],
    relevant_documents: list[str],
) -> float:
    """
    Reciprocal Rank:

        1 / rank of first relevant result
    """

    relevant = set(
        relevant_documents
    )

    for rank, document_id in enumerate(
        unique_document_ids(
            retrieved_documents
        ),
        start=1,
    ):

        if document_id in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    rankings: list[float],
) -> float:
    """
    Mean Reciprocal Rank across queries.
    """

    if not rankings:
        return 0.0

    return sum(rankings) / len(rankings)

def document_diversity_at_k(
    retrieved_documents: list[str],
    k: int,
) -> float:
    """
    Fraction of unique documents among the actual top-k results.
    Measures the fraction of unique documents among top-k results.

    Example:
        [A, B, B, C, D] → 4 unique documents / 5 results = 0.8
    """

    top_k = retrieved_documents[:k]
    print(retrieved_documents)

    if not top_k:
        return 0.0

    unique_documents = len(
        set(top_k)
    )
    # print(unique_documents)

    return unique_documents / len(top_k)