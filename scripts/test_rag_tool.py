from app.tools.documentation import (
    search_documentation,
)


def main() -> None:

    queries = [
        (
            "Why could customers be charged twice "
            "after a payment timeout?",
            "payment",
        ),
        (
            "How should API latency incidents "
            "be investigated?",
            "api_gateway",
        ),
        (
            "Why do authentication failures happen "
            "after key rotation?",
            "auth",
        ),
    ]

    for query, service in queries:

        print("\n" + "=" * 90)
        print("QUERY")
        print("=" * 90)

        print(query)

        print("\n" + "-" * 90)
        print("RETRIEVED EVIDENCE")
        print("-" * 90)

        result = search_documentation.invoke(
            {
                "query": query,
                "service": service,
            }
        )

        print(result)


if __name__ == "__main__":
    main()