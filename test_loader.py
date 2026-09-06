from app.retrieval.config import retrieval_config
from app.retrieval.loader import KnowledgeBaseLoader


def main() -> None:

    loader = KnowledgeBaseLoader(
        retrieval_config.knowledge_base_dir
    )

    documents = loader.load()

    print("=" * 70)
    print("KNOWLEDGE BASE LOADER TEST")
    print("=" * 70)

    print(f"Knowledge base:")
    print(retrieval_config.knowledge_base_dir)

    print(f"\nDocuments loaded: {len(documents)}")

    print("\nFirst 5 documents:")

    for i, document in enumerate(
        documents[:5],
        start=1,
    ):
        print("\n" + "-" * 70)

        print(f"Document #{i}")

        print(
            f"Source: "
            f"{document.metadata.get('source')}"
        )

        print(
            f"Document ID: "
            f"{document.metadata.get('document_id')}"
        )

        print(
            f"Category: "
            f"{document.metadata.get('category')}"
        )

        print(
            f"Type: "
            f"{document.metadata.get('document_type')}"
        )

        print("\nContent preview:")

        print(
            document.page_content[:500]
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()