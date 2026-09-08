from __future__ import annotations

from time import perf_counter
from typing import Optional

from app.retrieval.retriever import DocumentRetriever
from app.retrieval.schemas import RetrievalResponse

class RetrievalPipeline:
    """
    Public retrieval interface.

    This is intentionally separate from DocumentRetriever so
    future stages such as query rewriting, reranking,
    compression, caching and evaluation can be inserted
    without changing the agent/tool interface.
    """

    def __init__(
        self,
        retriever: Optional[DocumentRetriever] = None,
    ) -> None:

        self.retriever = (
            retriever
            if retriever is not None
            else DocumentRetriever()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        service: Optional[str] = None,
        category: Optional[str] = None,
    ) -> RetrievalResponse:

        start = perf_counter()

        response = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            service=service,
            category=category,
        )

        elapsed_ms = (
            perf_counter() - start
        ) * 1000

        response.retrieval_time_ms = (
            round(elapsed_ms, 3)
        )

        return response

# x= RetrievalPipeline()
# z = x.retrieve(query="How should webhook delivery failures be investigated?",top_k=5,service="webhook").results
# print(len(z),' \n')
# # print(z[0].content,' \n')
# p = z[0].document_id
# for i in p:
#     print(i)