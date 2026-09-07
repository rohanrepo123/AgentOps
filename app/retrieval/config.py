from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RetrievalConfig:
    """
    Configuration for the document retrieval pipeline.

    Keeping retrieval settings in one place makes it easy to run
    experiments later with different chunk sizes, top-k values,
    embedding models, etc.
    """

    # ---------------------------------------------------------
    # Project paths
    # ---------------------------------------------------------

    project_root: Path = (
    Path(__file__).resolve().parents[2]
    )
    knowledge_base_dir: Path = (
        project_root / "data" / "knowledge_base"
    )

    vector_store_dir: Path = (
        project_root / "data" / "vectorstore"
    )

    # ---------------------------------------------------------
    # Chunking
    # ---------------------------------------------------------

    chunk_size: int = 500
    chunk_overlap: int = 75

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    top_k: int = 5

    # Number of candidates retrieved before
    # optional reranking.
    candidate_k: int = 15

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    # embedding_model: str = "gemini-embedding-001"
    embedding_model: str = (
    "BAAI/bge-small-en-v1.5"
)
#     embedding_model: str = (
#     "text-embedding-3-large"
# )
#     embedding_model: str = (
#     "text-embedding-3-small"
# )
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="gemini-embedding-001"
# )

    # ---------------------------------------------------------
    # Retrieval thresholds
    # ---------------------------------------------------------

    # FAISS similarity score interpretation depends on the
    # index/retriever configuration, so this will not be used
    # blindly. It is here for future experiments.
    min_score: float = 0.0

    # ---------------------------------------------------------
    # Runtime options
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Retrieval improvements
    # ---------------------------------------------------------

    use_metadata_filtering: bool = True
    use_reranker: bool = False

    # Diversification experiment
    use_diversification: bool = True
    max_chunks_per_document: int = 1
    
# Single shared configuration object
retrieval_config = RetrievalConfig()