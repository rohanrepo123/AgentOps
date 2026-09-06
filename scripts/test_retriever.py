from app.retrieval.retriever import DocumentRetriever


def print_results(
    title: str,
    response,
) -> None:

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    print(f"\nQuery:")
    print(response.query)

    print(
        f"\nResults: "
        f"{response.total_results}"
    )

    for index, result in enumerate(
        response.results,
        start=1,
    ):

        print("\n" + "-" * 80)

        print(f"Rank       : {index}")
        print(f"Score      : {result.score:.4f}")
        print(
            f"Document ID: "
            f"{result.document_id}"
        )
        print(
            f"Chunk ID   : "
            f"{result.chunk_id}"
        )
        print(
            f"Category   : "
            f"{result.category}"
        )
        print(
            f"Type       : "
            f"{result.document_type}"
        )
        print(
            f"Service    : "
            f"{result.service}"
        )
        print(
            f"Source     : "
            f"{result.source}"
        )

        print("\nContent:")
        print(
            result.content[:1000]
        )


def main() -> None:

    retriever = DocumentRetriever()

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    response = retriever.retrieve(
        query=(
            "Why could customers be charged twice "
            "after a payment timeout?"
        )
    )

    print_results(
        "TEST 1: DUPLICATE PAYMENT",
        response,
    )

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    response = retriever.retrieve(
        query=(
            "How should a payment timeout "
            "be investigated?"
        )
    )

    print_results(
        "TEST 2: PAYMENT TIMEOUT",
        response,
    )

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    response = retriever.retrieve(
        query=(
            "What causes elevated API latency?"
        )
    )

    print_results(
        "TEST 3: API LATENCY",
        response,
    )

    # --------------------------------------------------------
    # Test 4
    # --------------------------------------------------------

    response = retriever.retrieve(
        query=(
            "Why are users getting authentication "
            "failures after key rotation?"
        )
    )

    print_results(
        "TEST 4: AUTHENTICATION",
        response,
    )

    # --------------------------------------------------------
    # Test 5
    # --------------------------------------------------------

    response = retriever.retrieve(
        query=(
            "What should I check when notification "
            "queues become saturated?"
        )
    )

    print_results(
        "TEST 5: NOTIFICATION BACKLOG",
        response,
    )

    # --------------------------------------------------------
    # Test metadata filtering
    # --------------------------------------------------------

    response = retriever.retrieve(
        query="retry after payment timeout",
        service="payment",
    )

    print_results(
        "TEST 6: PAYMENT SERVICE FILTER",
        response,
    )


if __name__ == "__main__":
    main()