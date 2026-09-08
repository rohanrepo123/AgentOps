# Used for document retrieval during query processing.
from __future__ import annotations

from typing import Optional
# from app.retrieval.query_expander import SimpleQueryExpander
from app.retrieval.multi_query_expander import MultiQueryExpander
from langchain_community.vectorstores import FAISS

from app.retrieval.config import retrieval_config
from app.retrieval.diversifier import DocumentDiversifier
from app.retrieval.reranker import DocumentReranker
from app.retrieval.schemas import RetrievalResponse, RetrievalResult
from app.retrieval.vector_store import FAISSVectorStore


class DocumentRetriever:
    """High-level retrieval interface for the AcmeCloud knowledge base."""

    def __init__(
        self,
        vector_store: Optional[FAISS] = None,
        use_reranker: Optional[bool] = None,
        #Added
        use_query_expansion: Optional[bool] = None,
        use_multi_query_expansion: Optional[bool] = None
    ) -> None:
        self.diversifier = DocumentDiversifier(
            max_chunks_per_document=retrieval_config.max_chunks_per_document
        )
        self.use_query_expansion = (
            retrieval_config.use_query_expansion
            if use_query_expansion is None
            else use_query_expansion
        )

        self.use_multi_query_expansion = (
            False
            if use_multi_query_expansion is None
            else use_multi_query_expansion
        )

        if self.use_query_expansion and self.use_multi_query_expansion:
            raise ValueError(
                "use_query_expansion and use_multi_query_expansion "
                "cannot both be enabled."
            )

        self.query_expander = None
        self.multi_query_expander = None

        if self.use_query_expansion:
            from app.retrieval.query_expander import SimpleQueryExpander

            self.query_expander = SimpleQueryExpander()

        if self.use_multi_query_expansion:
            self.multi_query_expander = MultiQueryExpander()

        self.use_reranker = (
            retrieval_config.use_reranker
            if use_reranker is None
            else use_reranker
        )
        self.reranker = DocumentReranker() if self.use_reranker else None

        if vector_store is not None:
            self.vector_store = vector_store
        else:
            manager = FAISSVectorStore(retrieval_config.vector_store_dir)
            if not manager.exists():
                raise FileNotFoundError(
                    "FAISS vector store was not found.\n"
                    "Run:\n"
                    "python scripts/build_vectorstore.py"
                )
            self.vector_store = manager.load()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        service: Optional[str] = None,
        category: Optional[str] = None,
    ) -> RetrievalResponse:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        top_k = top_k if top_k is not None else retrieval_config.top_k
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        original_query = query

        # if self.query_expander is not None:
        #     retrieval_query = self.query_expander.expand(query)
        # else:
        #     retrieval_query = query


        # search_k = max(top_k, retrieval_config.candidate_k)

        # raw_results = self.vector_store.similarity_search_with_score(
        #     retrieval_query,
        #     k=search_k,
        # )


        # ---------------------------------------------------------
        # Build retrieval queries
        # ---------------------------------------------------------

        if self.multi_query_expander is not None:

            retrieval_queries = self.multi_query_expander.expand(
                original_query
            )

        elif self.query_expander is not None:

            retrieval_queries = [
                self.query_expander.expand(original_query)
            ]

        else:

            retrieval_queries = [original_query]


        # ---------------------------------------------------------
        # Retrieve candidates for every query variant
        # ---------------------------------------------------------

        search_k = max(
            top_k,
            retrieval_config.candidate_k,
        )

        candidate_map: dict[tuple[str, str], RetrievalResult] = {}

        for retrieval_query in retrieval_queries:

            raw_results = (
                self.vector_store.similarity_search_with_score(
                    retrieval_query,
                    k=search_k,
                )
            )

            for document, score in raw_results:

                metadata = document.metadata

                # -----------------------------
                # Metadata filtering
                # -----------------------------

                if service is not None:

                    document_service = metadata.get(
                        "service"
                    )

                    related_services = metadata.get(
                        "related_services",
                        [],
                    )

                    if (
                        document_service != service
                        and service not in related_services
                    ):
                        continue

                if (
                    category is not None
                    and metadata.get("category") != category
                ):
                    continue

                result = RetrievalResult(
                    content=document.page_content,
                    score=float(score),
                    document_id=str(
                        metadata.get(
                            "document_id",
                            "unknown",
                        )
                    ),
                    source=str(
                        metadata.get(
                            "source",
                            "unknown",
                        )
                    ),
                    category=str(
                        metadata.get(
                            "category",
                            "unknown",
                        )
                    ),
                    document_type=str(
                        metadata.get(
                            "document_type",
                            "unknown",
                        )
                    ),
                    service=metadata.get("service"),
                    chunk_id=metadata.get("chunk_id"),
                    metadata=metadata,
                )

                identity = (
                    result.document_id,
                    result.chunk_id or "",
                )

                # Keep the best FAISS score for each chunk.
                existing = candidate_map.get(identity)

                if existing is None or result.score < existing.score:
                    candidate_map[identity] = result


        candidates = list(candidate_map.values())



        candidates: list[RetrievalResult] = []

        for document, score in raw_results:
            metadata = document.metadata

            if service is not None:
                document_service = metadata.get("service")
                related_services = metadata.get("related_services", [])
                if (
                    document_service != service
                    and service not in related_services
                ):
                    continue

            if (
                category is not None
                and metadata.get("category") != category
            ):
                continue

            candidates.append(
                RetrievalResult(
                    content=document.page_content,
                    score=float(score),
                    document_id=str(metadata.get("document_id", "unknown")),
                    source=str(metadata.get("source", "unknown")),
                    category=str(metadata.get("category", "unknown")),
                    document_type=str(metadata.get("document_type", "unknown")),
                    service=metadata.get("service"),
                    chunk_id=metadata.get("chunk_id"),
                    metadata=metadata,
                )
            )

        # Apply reranker to the full candidate pool.
        if self.reranker is not None:
            ranked_candidates = self.reranker.rerank(
                query=original_query,
                candidates=candidates,
                top_k=None,
            )
        else:
            ranked_candidates = candidates


        # Apply diversification only to the final ranking.
        if retrieval_config.use_diversification:
            results = self.diversifier.diversify(
                ranked_candidates,
                top_k=top_k,
            )
        else:
            results = ranked_candidates[:top_k]

        return RetrievalResponse(
            query=original_query,
            retrieval_queries=retrieval_queries,
            results=results,
            total_results=len(results[:top_k]),
        )
