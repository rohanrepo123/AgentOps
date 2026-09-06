from app.retrieval.config import retrieval_config
from app.retrieval.loader import KnowledgeBaseLoader


def main() -> None:

    loader = KnowledgeBaseLoader(
        retrieval_config.knowledge_base_dir
    )

    documents = loader.load()

    print("=" * 80)
    print("KNOWLEDGE BASE METADATA")
    print("=" * 80)

    for document in documents[:10]:

        print("\n" + "-" * 80)

        print(
            "Source:",
            document.metadata.get("source")
        )

        print(
            "Document ID:",
            document.metadata.get(
                "document_id"
            )
        )

        print(
            "Category:",
            document.metadata.get(
                "category"
            )
        )

        print(
            "Type:",
            document.metadata.get(
                "document_type"
            )
        )

        print(
            "Service:",
            document.metadata.get(
                "service"
            )
        )

        print(
            "Version:",
            document.metadata.get(
                "version"
            )
        )


if __name__ == "__main__":
    main()