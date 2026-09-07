#Used for Document Retrieval during Query asking
from __future__ import annotations

from typing import Optional

from langchain_community.vectorstores import FAISS

from app.retrieval.diversifier import (
    DocumentDiversifier,
)
from app.retrieval.config import retrieval_config
from app.retrieval.schemas import (
    RetrievalResponse,
    RetrievalResult,
)
from app.retrieval.vector_store import FAISSVectorStore

class DocumentRetriever:
    """
    High-level retrieval interface for the AcmeCloud knowledge base.

    The rest of the application should interact with this class
    rather than directly calling FAISS.
    """

    def __init__(
        self,
        vector_store: Optional[FAISS] = None,
    ) -> None:
        self.diversifier = DocumentDiversifier(
        max_chunks_per_document=(
            retrieval_config.max_chunks_per_document
            )
        )
        if vector_store is not None:
            self.vector_store = vector_store

        else:
            manager = FAISSVectorStore(
                retrieval_config.vector_store_dir
            )

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
            raise ValueError(
                "Query cannot be empty."
            )

        top_k = (
            top_k
            if top_k is not None
            else retrieval_config.top_k
        )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        search_k = max(
            top_k,
            retrieval_config.candidate_k              )

        raw_results = (
            self.vector_store
            .similarity_search_with_score(
                query,
                k=search_k,
            )
        )

        candidates: list[RetrievalResult] = []

        for document, score in raw_results:

            metadata = document.metadata

            if service is not None:
                document_service = metadata.get('service')
                related_services = metadata.get('related_services',[])
                if (document_service != service
                    and service not in related_services):
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
                    service=metadata.get(
                        "service"
                    ),
                    chunk_id=metadata.get(
                        "chunk_id"
                    ),
                    metadata=metadata,
                )
            )

        # ---------------------------------------------------------
        # Diversification
        # ---------------------------------------------------------

        if retrieval_config.use_diversification:

            results = self.diversifier.diversify(
                candidates,
                top_k=top_k,
            )

        else:

            results = candidates[:top_k]


        return RetrievalResponse(
            query=query,
            results=results,
            total_results=len(results),
        )