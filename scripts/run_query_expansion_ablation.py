"""
Run a controlled query expansion OFF vs ON ablation.

The only intended experimental change is use_query_expansion.

Fixed:
  candidate_k=20
  top_k=5
  reranking=True
  metadata filtering=True
  diversification=True
  max_chunks_per_document=1
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from time import perf_counter

import numpy as np

from app.retrieval.config import RetrievalConfig
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.retriever import DocumentRetriever


def reciprocal_rank(results, relevant_documents):
    for rank, result in enumerate(results, start=1):
        if result.document_id in relevant_documents:
            return 1.0 / rank
    return 0.0


def hit_at_k(results, relevant_documents):
    return float(
        any(r.document_id in relevant_documents for r in results)
    )


def precision_at_k(results, relevant_documents, k):
    if not results:
        return 0.0

    retrieved_documents = {
        r.document_id
        for r in results[:k]
    }

    relevant_documents = set(relevant_documents)

    return (
        len(retrieved_documents & relevant_documents)
        / len(retrieved_documents)
    )


def recall_at_k(results, relevant_documents, k):
    if not relevant_documents:
        return 0.0

    retrieved_documents = {
        r.document_id
        for r in results[:k]
    }

    relevant_documents = set(relevant_documents)

    return (
        len(retrieved_documents & relevant_documents)
        / len(relevant_documents)
    )


def diversity_at_k(results, k):
    selected = results[:k]

    if not selected:
        return 0.0

    return (
        len({r.document_id for r in selected})
        / len(selected)
    )


def load_cases(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def run(cases, use_query_expansion: bool):

    retriever = DocumentRetriever(
        use_reranker=True,
        use_query_expansion=use_query_expansion,
    )

    pipeline = RetrievalPipeline(
        retriever=retriever
    )

    latencies = []
    rows = []

    for case in cases:

        start = perf_counter()

        response = pipeline.retrieve(
            case["query"],
            top_k=5,
            service=case.get("service"),
            category=case.get("category"),
        )

        elapsed_ms = (
            perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

        relevant = set(
            case["relevant_documents"]
        )

        results = response.results

        rows.append(
            {
                "query": case["query"],

                "retrieval_query": response.new_query,

                "recall_at_1": recall_at_k(
                    results,
                    relevant,
                    1,
                ),

                "recall_at_3": recall_at_k(
                    results,
                    relevant,
                    3,
                ),

                "recall_at_5": recall_at_k(
                    results,
                    relevant,
                    5,
                ),

                "precision_at_1": precision_at_k(
                    results,
                    relevant,
                    1,
                ),

                "precision_at_3": precision_at_k(
                    results,
                    relevant,
                    3,
                ),

                "precision_at_5": precision_at_k(
                    results,
                    relevant,
                    5,
                ),

                "hit_at_1": hit_at_k(
                    results[:1],
                    relevant,
                ),

                "hit_at_3": hit_at_k(
                    results[:3],
                    relevant,
                ),

                "hit_at_5": hit_at_k(
                    results[:5],
                    relevant,
                ),

                "mrr": reciprocal_rank(
                    results,
                    relevant,
                ),

                "diversity_at_5": diversity_at_k(
                    results,
                    5,
                ),

                "latency_ms": elapsed_ms,

                "documents": [
                    r.document_id
                    for r in results
                ],
            }
        )

    def mean(key):
        return statistics.mean(
            row[key]
            for row in rows
        )

    return {
        "use_query_expansion":
            use_query_expansion,

        "use_reranker": True,

        "candidate_k":
            RetrievalConfig().candidate_k,

        "top_k": 5,

        "mean_retrieval_latency_ms":
            mean("latency_ms"),

        "p95_retrieval_latency_ms":
            float(
                np.percentile(
                    latencies,
                    95,
                )
            ),

        "recall_at_1":
            mean("recall_at_1"),

        "recall_at_3":
            mean("recall_at_3"),

        "recall_at_5":
            mean("recall_at_5"),

        "precision_at_1":
            mean("precision_at_1"),

        "precision_at_3":
            mean("precision_at_3"),

        "precision_at_5":
            mean("precision_at_5"),

        "hit_rate_at_1":
            mean("hit_at_1"),

        "hit_rate_at_3":
            mean("hit_at_3"),

        "hit_rate_at_5":
            mean("hit_at_5"),

        "mrr":
            mean("mrr"),

        "diversity_at_5":
            mean("diversity_at_5"),

        "per_query": rows,
    }


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(
            "data/datasets/retrieval_eval.json"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/retrieval/"
            "query_expansion/results.json"
        ),
    )

    args = parser.parse_args()

    cases = load_cases(args.cases)

    baseline = run(
        cases,
        use_query_expansion=False,
    )

    expanded = run(
        cases,
        use_query_expansion=True,
    )

    output = {
        "baseline": baseline,
        "query_expanded": expanded,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
print("=" * 80)
print("QUERY EXPANSION ABLATION")
print("=" * 80)

for name, result in output.items():

    print()
    print(name.upper())
    print("-" * 80)

    print(
        f"Query Expansion      = "
        f"{result['use_query_expansion']}"
    )

    print(
        f"Reranker             = "
        f"{result['use_reranker']}"
    )

    print(
        f"Candidate K          = "
        f"{result['candidate_k']}"
    )

    print(
        f"Top K                = "
        f"{result['top_k']}"
    )

    print()

    print(
        f"Recall@1             = "
        f"{result['recall_at_1']:.4f}"
    )

    print(
        f"Recall@3             = "
        f"{result['recall_at_3']:.4f}"
    )

    print(
        f"Recall@5             = "
        f"{result['recall_at_5']:.4f}"
    )

    print(
        f"Precision@1          = "
        f"{result['precision_at_1']:.4f}"
    )

    print(
        f"Precision@3          = "
        f"{result['precision_at_3']:.4f}"
    )

    print(
        f"Precision@5          = "
        f"{result['precision_at_5']:.4f}"
    )

    print(
        f"HitRate@1            = "
        f"{result['hit_rate_at_1']:.4f}"
    )

    print(
        f"HitRate@3            = "
        f"{result['hit_rate_at_3']:.4f}"
    )

    print(
        f"HitRate@5            = "
        f"{result['hit_rate_at_5']:.4f}"
    )

    print(
        f"MRR                  = "
        f"{result['mrr']:.4f}"
    )

    print(
        f"Diversity@5          = "
        f"{result['diversity_at_5']:.4f}"
    )

    print()

    print(
        f"Mean Latency         = "
        f"{result['mean_retrieval_latency_ms']:.3f} ms"
    )

    print(
        f"P95 Latency          = "
        f"{result['p95_retrieval_latency_ms']:.3f} ms"
    )

print()
print("=" * 80)
print(
    f"Results saved to: {args.output}"
)
print("=" * 80)