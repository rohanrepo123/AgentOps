from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.retriever import DocumentRetriever
from app.evaluation.datasets import (
    load_retrieval_dataset,
)

RESULTS_PATH = Path(
    "experiments/retrieval/reranking/results.json"
)

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "datasets"
    / "retrieval_eval.json"
)

def load_dataset() -> list[dict]:
    """
    Load the existing retrieval evaluation dataset.

    Replace this implementation with the same dataset-loading
    logic already used by your existing ablation script.
    """
    dataset = load_retrieval_dataset(
            DATASET_PATH
        )
    return dataset
    # raise NotImplementedError(
    #     "Reuse the dataset loader from the existing "
    #     "retrieval ablation script."
    # )


def unique_document_ids(results) -> set[str]:
    return {
        result.document_id
        for result in results
    }


def recall_at_k(
    results,
    relevant_documents,
    k: int,
) -> float:

    relevant = set(relevant_documents)

    if not relevant:
        return 0.0

    retrieved = unique_document_ids(
        results[:k]
    )

    return len(
        retrieved & relevant
    ) / len(relevant)


def precision_at_k(
    results,
    relevant_documents,
    k: int,
) -> float:

    retrieved = unique_document_ids(
        results[:k]
    )

    relevant = set(relevant_documents)

    if not retrieved:
        return 0.0

    return len(
        retrieved & relevant
    ) / len(retrieved)


def hit_at_k(
    results,
    relevant_documents,
    k: int,
) -> float:

    relevant = set(relevant_documents)

    retrieved = unique_document_ids(
        results[:k]
    )

    return float(
        bool(retrieved & relevant)
    )


def reciprocal_rank(
    results,
    relevant_documents,
) -> float:

    relevant = set(relevant_documents)

    for index, result in enumerate(
        results,
        start=1,
    ):

        if result.document_id in relevant:
            return 1.0 / index

    return 0.0


def diversity_at_k(
    results,
    k: int,
) -> float:

    if not results:
        return 0.0

    selected = results[:k]

    unique_documents = {
        result.document_id
        for result in selected
    }

    return len(unique_documents) / len(selected)


def evaluate(
    dataset: list[dict],
    use_multi_query_expansion: bool,
) -> dict:

    retriever = DocumentRetriever(
        use_reranker=True,
        use_query_expansion=False,
        use_multi_query_expansion=(
            use_multi_query_expansion
        ),
    )

    pipeline = RetrievalPipeline(
        retriever=retriever
    )

    per_query = []

    for item in dataset:

        query = item.query
        # item['']

        relevant_documents = item.relevant_documents
        

        response = pipeline.retrieve(
            query=query,
            top_k=5,
        )

        results = response.results

        per_query.append(
            {
                "query": query,
                "retrieval_queries": (
                    response.retrieval_queries
                ),
                "recall_at_1": recall_at_k(
                    results,
                    relevant_documents,
                    1,
                ),
                "recall_at_3": recall_at_k(
                    results,
                    relevant_documents,
                    3,
                ),
                "recall_at_5": recall_at_k(
                    results,
                    relevant_documents,
                    5,
                ),
                "precision_at_1": precision_at_k(
                    results,
                    relevant_documents,
                    1,
                ),
                "precision_at_3": precision_at_k(
                    results,
                    relevant_documents,
                    3,
                ),
                "precision_at_5": precision_at_k(
                    results,
                    relevant_documents,
                    5,
                ),
                "hit_rate_at_1": hit_at_k(
                    results,
                    relevant_documents,
                    1,
                ),
                "hit_rate_at_3": hit_at_k(
                    results,
                    relevant_documents,
                    3,
                ),
                "hit_rate_at_5": hit_at_k(
                    results,
                    relevant_documents,
                    5,
                ),
                "mrr": reciprocal_rank(
                    results,
                    relevant_documents,
                ),
                "diversity_at_5": diversity_at_k(
                    results,
                    5,
                ),
                "retrieval_time_ms": (
                    response.retrieval_time_ms
                ),
                "documents": [
                    result.document_id
                    for result in results
                ],
            }
        )

    return {
        "use_multi_query_expansion": (
            use_multi_query_expansion
        ),
        "candidate_k": 20,
        "top_k": 5,
        "mean_retrieval_latency_ms": mean(
            item["retrieval_time_ms"]
            for item in per_query
        ),
        "recall_at_1": mean(
            item["recall_at_1"]
            for item in per_query
        ),
        "recall_at_3": mean(
            item["recall_at_3"]
            for item in per_query
        ),
        "recall_at_5": mean(
            item["recall_at_5"]
            for item in per_query
        ),
        "precision_at_1": mean(
            item["precision_at_1"]
            for item in per_query
        ),
        "precision_at_3": mean(
            item["precision_at_3"]
            for item in per_query
        ),
        "precision_at_5": mean(
            item["precision_at_5"]
            for item in per_query
        ),
        "hit_rate_at_1": mean(
            item["hit_rate_at_1"]
            for item in per_query
        ),
        "hit_rate_at_3": mean(
            item["hit_rate_at_3"]
            for item in per_query
        ),
        "hit_rate_at_5": mean(
            item["hit_rate_at_5"]
            for item in per_query
        ),
        "mrr": mean(
            item["mrr"]
            for item in per_query
        ),
        "diversity_at_5": mean(
            item["diversity_at_5"]
            for item in per_query
        ),
        "per_query": per_query,
    }


def main() -> None:

    dataset = load_dataset()

    baseline = evaluate(
        dataset,
        use_multi_query_expansion=False,
    )

    multi_query = evaluate(
        dataset,
        use_multi_query_expansion=True,
    )

    output = {
        "baseline": baseline,
        "multi_query": multi_query,
    }

    output_path = Path(
        "experiments/retrieval/reranking/"
        "multi_query_results.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print(
        f"\nResults saved to: {output_path}"
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()