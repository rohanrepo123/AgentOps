from __future__ import annotations

from functools import lru_cache
from typing import Optional

from langchain_core.tools import tool

from app.retrieval.pipeline import RetrievalPipeline


@lru_cache(maxsize=1)
def get_retrieval_pipeline() -> RetrievalPipeline:
    """
    Create one shared retrieval pipeline.

    This prevents the FAISS index from being reloaded for
    every tool invocation.
    """

    return RetrievalPipeline()


@tool
def search_documentation(
    query: str,
    service: Optional[str] = None,
) -> str:
    """
    Search AcmeCloud engineering documentation.

    Use this tool for questions involving:
    - architecture
    - services
    - APIs
    - runbooks
    - troubleshooting
    - historical incidents

    Do NOT use this tool for live database state,
    operational metrics or raw production logs.
    """

    pipeline = get_retrieval_pipeline()

    response = pipeline.retrieve(
        query=query,
        top_k=5,
        service=service,
    )

    if not response.results:
        return (
            "No relevant documentation was found "
            "for the given query."
        )

    output: list[str] = []

    for index, result in enumerate(
        response.results,
        start=1,
    ):

        output.append(
            "\n".join(
                [
                    f"[Evidence {index}]",
                    f"Source: {result.source}",
                    f"Document: {result.document_id}",
                    f"Section: {result.metadata.get('section', 'unknown')}",
                    f"Service: {result.service}",
                    "",
                    result.content,
                ]
            )
        )

    return "\n\n".join(output)