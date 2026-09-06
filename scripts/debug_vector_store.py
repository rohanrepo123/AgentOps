from app.retrieval.config import retrieval_config
from app.retrieval.vector_store import FAISSVectorStore


def main() -> None:

    print("=" * 80)
    print("VECTOR STORE DEBUG")
    print("=" * 80)

    print("\nVector store directory:")
    print(retrieval_config.vector_store_dir)

    manager = FAISSVectorStore(
        retrieval_config.vector_store_dir
    )

    print("\nIndex exists:")
    print(manager.exists())

    if not manager.exists():
        raise RuntimeError(
            "FAISS index does not exist."
        )

    vectorstore = manager.load()

    print("\nFAISS object loaded:")
    print(type(vectorstore))

    print("\nDocument store size:")

    try:
        print(
            len(vectorstore.docstore._dict)
        )
    except Exception as exc:
        print(
            "Could not inspect docstore:",
            exc
        )

    print("\nIndex size:")

    try:
        print(
            vectorstore.index.ntotal
        )
    except Exception as exc:
        print(
            "Could not inspect FAISS index:",
            exc
        )

    # -------------------------------------------------------
    # Direct similarity test
    # -------------------------------------------------------

    queries = [
        "Why could customers be charged twice after a payment timeout?",
        "How should API latency incidents be investigated?",
        "Why do authentication failures happen after key rotation?",
    ]

    for query in queries:

        print("\n" + "=" * 80)
        print("QUERY")
        print("=" * 80)

        print(query)

        try:
            results = (
                vectorstore
                .similarity_search_with_score(
                    query,
                    k=5,
                )
            )

            print(
                f"\nRaw FAISS results: {len(results)}"
            )

            for i, (doc, score) in enumerate(
                results,
                start=1,
            ):

                print("\n" + "-" * 80)

                print("Rank:", i)
                print("Score:", score)

                print(
                    "Document ID:",
                    doc.metadata.get(
                        "document_id"
                    )
                )

                print(
                    "Source:",
                    doc.metadata.get(
                        "source"
                    )
                )

                print(
                    "Category:",
                    doc.metadata.get(
                        "category"
                    )
                )

                print(
                    "Service:",
                    doc.metadata.get(
                        "service"
                    )
                )

                print(
                    "Chunk:",
                    doc.metadata.get(
                        "chunk_id"
                    )
                )

                print("\nContent:")
                print(
                    doc.page_content[:500]
                )

        except Exception as exc:

            print(
                "\nSimilarity search failed:"
            )

            print(
                type(exc).__name__,
                exc
            )


if __name__ == "__main__":
    main()
    