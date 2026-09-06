from app.retrieval.config import retrieval_config
from app.retrieval.vector_store import FAISSVectorStore


def main() -> None:

    manager = FAISSVectorStore(
        retrieval_config.vector_store_dir
    )

    vectorstore = manager.load()

    documents = (
        vectorstore.docstore._dict.values()
    )

    print("=" * 80)
    print("VECTOR STORE DOCUMENT INVENTORY")
    print("=" * 80)

    print(
        f"\nTotal chunks: "
        f"{len(documents)}"
    )

    unique_documents = {}

    for document in documents:

        document_id = document.metadata.get(
            "document_id"
        )

        if document_id not in unique_documents:
            unique_documents[
                document_id
            ] = {
                "source": document.metadata.get(
                    "source"
                ),
                "category": document.metadata.get(
                    "category"
                ),
                "service": document.metadata.get(
                    "service"
                ),
            }

    print(
        f"Unique documents: "
        f"{len(unique_documents)}"
    )

    for document_id, metadata in sorted(
        unique_documents.items()
    ):

        print(
            f"\n{document_id}"
        )

        print(
            f"  Source   : "
            f"{metadata['source']}"
        )

        print(
            f"  Category : "
            f"{metadata['category']}"
        )

        print(
            f"  Service  : "
            f"{metadata['service']}"
        )


if __name__ == "__main__":
    main()