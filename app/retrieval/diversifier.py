from __future__ import annotations

from typing import Iterable

from app.retrieval.schemas import RetrievalResult


class DocumentDiversifier:
    """
    Reduces repeated chunks from the same source document.

    The retriever first obtains a larger candidate pool, then this
    class selects a diverse set of documents for the final context.
    """

    def __init__(
        self,
        max_chunks_per_document: int = 1,
    ) -> None:

        if max_chunks_per_document <= 0:
            raise ValueError(
                "max_chunks_per_document must be greater than 0."
            )

        self.max_chunks_per_document = (
            max_chunks_per_document
        )

    def diversify(
        self,
        results: Iterable[RetrievalResult],
        top_k: int,
    ) -> list[RetrievalResult]:

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        results = list(results)

        selected: list[RetrievalResult] = []

        document_counts: dict[str, int] = {}

        # First pass:
        # Prefer one chunk per unique document.
        for result in results:

            document_id = result.document_id

            count = document_counts.get(
                document_id,
                0,
            )   
            # print(18*"Diversity.py",'\n')

            if count >= self.max_chunks_per_document:
                continue

            selected.append(result)

            document_counts[document_id] = (
                count + 1
            )

            if len(selected) >= top_k:
                break

        # Second pass:
        # If there are not enough unique documents,
        # fill the remaining slots with additional chunks.
        if len(selected) < top_k:

            selected_chunk_ids = {
                (
                    result.document_id,
                    result.chunk_id,
                )
                for result in selected
            }

            for result in results:

                identity = (
                    result.document_id,
                    result.chunk_id,
                )

                if identity in selected_chunk_ids:
                    continue

                selected.append(result)

                selected_chunk_ids.add(identity)

                if len(selected) >= top_k:
                    break

        return selected
# 1. First Pass (Strict Diversity)
# Iterates through candidate results in their original ranked order.

# Tracks how many chunks have been selected from each document_id.

# Allows at most max_chunks_per_document (default = 1) per document.

# If a document has already hit the limit, its subsequent chunks are skipped.

# Stops immediately once it collects top_k unique results.