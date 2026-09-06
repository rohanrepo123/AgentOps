from app.retrieval.chunker import (
    KnowledgeBaseChunker,
)
from app.retrieval.config import retrieval_config
from app.retrieval.loader import (
    KnowledgeBaseLoader,
)
from app.retrieval.vector_store import (
    FAISSVectorStore,
)


def main() -> None:

    print("=" * 70)
    print("AGENTOPS VECTOR STORE BUILDER")
    print("=" * 70)

    # -------------------------------------------------------
    # 1. Load documents
    # -------------------------------------------------------

    print("\n[1/4] Loading knowledge base...")

    loader = KnowledgeBaseLoader(
        retrieval_config.knowledge_base_dir
    )

    documents = loader.load()

    print(
        f"Loaded documents: {len(documents)}"
    )

    # -------------------------------------------------------
    # 2. Chunk documents
    # -------------------------------------------------------

    print("\n[2/4] Chunking documents...")

    chunker = KnowledgeBaseChunker(
        chunk_size=retrieval_config.chunk_size,
        chunk_overlap=retrieval_config.chunk_overlap,
    )

    chunks = chunker.chunk(documents)

    print(
        f"Generated chunks: {len(chunks)}"
    )

    # -------------------------------------------------------
    # 3. Build FAISS
    # -------------------------------------------------------

    print("\n[3/4] Building FAISS index...")

    vector_store = FAISSVectorStore(
        retrieval_config.vector_store_dir
    )

    vector_store.build(chunks)

    # -------------------------------------------------------
    # 4. Save
    # -------------------------------------------------------

    print("\n[4/4] Saving FAISS index...")

    vector_store.save()

    print(
        f"Saved to: "
        f"{retrieval_config.vector_store_dir}"
    )

    print("\n" + "=" * 70)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 70)

    print(f"\nDocuments : {len(documents)}")
    print(f"Chunks    : {len(chunks)}")
    print(
        f"Embedding : "
        f"{retrieval_config.embedding_model}"
    )
    print(
        f"Chunk size: "
        f"{retrieval_config.chunk_size}"
    )
    print(
        f"Overlap   : "
        f"{retrieval_config.chunk_overlap}"
    )


if __name__ == "__main__":
    main()
