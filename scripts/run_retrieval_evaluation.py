from __future__ import annotations
import json
from datetime import datetime, timezone
import statistics
from pathlib import Path
import numpy as np
from app.evaluation.datasets import (
    load_retrieval_dataset,
)

from app.evaluation.metrics import (
    document_diversity_at_k,
    hit_rate_at_k,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    unique_document_ids,
)
from app.retrieval.config import retrieval_config
from app.retrieval.pipeline import RetrievalPipeline

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

RESULTS_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "retrieval"
    / "diversification"
    / "results.jsonl"
)


DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "datasets"
    / "retrieval_eval.json"
)


K_VALUES = [1, 3, 5]

RESULTS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

def validate_ground_truth(
    dataset,
    pipeline,
) -> None:
    """
    Validate that all ground-truth document IDs
    exist in the FAISS document store.
    """

    available_ids: set[str] = set()

    vectorstore = (
        pipeline.retriever.vector_store
    )

    for document in (
        vectorstore.docstore._dict.values()
    ):

        document_id = (
            document.metadata.get(
                "document_id"
            )
        )

        if document_id:
            available_ids.add(
                str(document_id)
            )

    missing: dict[str, list[str]] = {}

    for case in dataset:

        missing_ids = [
            document_id
            for document_id
            in case.relevant_documents
            if document_id
            not in available_ids
        ]

        if missing_ids:
            missing[
                case.query_id
            ] = missing_ids

    if missing:

        print(
            "\nGROUND-TRUTH VALIDATION FAILED"
        )

        for query_id, ids in missing.items():

            print(
                f"{query_id}: "
                f"{ids}"
            )

        raise RuntimeError(
            "Some ground-truth document IDs do not "
            "exist in the vector store. Fix the dataset "
            "before evaluating."
        )


def main() -> None:

    print("=" * 80)
    print("AGENTOPS BASELINE RETRIEVAL EVALUATION")
    print("=" * 80)

    print(
        f"\nDataset: {DATASET_PATH}"
    )

    dataset = load_retrieval_dataset(
        DATASET_PATH
    )

    print(
        f"Evaluation queries: "
        f"{len(dataset)}"
    )

    pipeline = RetrievalPipeline()

    # --------------------------------------------------------
    # Validate dataset against vector store
    # --------------------------------------------------------

    print(
        "\nValidating ground-truth "
        "document IDs..."
    )

    validate_ground_truth(
        dataset,
        pipeline,
    )

    print(
        "Ground-truth validation: PASS"
    )

    # --------------------------------------------------------
    # Store metric values
    # --------------------------------------------------------

    recall_scores = {
        k: []
        for k in K_VALUES
    }

    precision_scores = {
        k: []
        for k in K_VALUES
    }

    hit_scores = {
        k: []
        for k in K_VALUES
    }
    diversity_scores = {
    k: []
    for k in K_VALUES
    }
    
    reciprocal_ranks = []

    retrieval_latencies = []

    # --------------------------------------------------------
    # Evaluate every query
    # --------------------------------------------------------

    for case_index, case in enumerate(
        dataset,
        start=1,
    ):

        response = pipeline.retrieve(
            query=case.query,
            service=case.service,
            top_k=max(K_VALUES),
        )

        retrieved_documents = [
            result.document_id
            for result in response.results
        ]

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        for k in K_VALUES:

            recall_scores[k].append(
                recall_at_k(
                    retrieved_documents,
                    case.relevant_documents,
                    k,
                )
            )

            precision_scores[k].append(
                precision_at_k(
                    retrieved_documents,
                    case.relevant_documents,
                    k,
                )
            )

            hit_scores[k].append(
                hit_rate_at_k(
                    retrieved_documents,
                    case.relevant_documents,
                    k,
                )
            )

            diversity_scores[k].append(
            document_diversity_at_k(
                retrieved_documents,
                k,
            )
        )
        reciprocal_ranks.append(
            reciprocal_rank(
                retrieved_documents,
                case.relevant_documents,
            )
        )

        retrieval_latencies.append(
            response.retrieval_time_ms
        )

        # ----------------------------------------------------
        # Per-query report
        # ----------------------------------------------------

        print(
            f"\n[{case_index}/{len(dataset)}] "
            f"{case.query_id}"
        )

        print(
            f"Query: {case.query}"
        )

        print(
            f"Service filter: "
            f"{case.service}"
        )

        print(
            f"Expected: "
            f"{case.relevant_documents}"
        )

        print(
            "Retrieved: "
            f"{unique_document_ids(retrieved_documents)}"
        )

        for k in K_VALUES:

            print(
                f"  Recall@{k}: "
                f"{recall_scores[k][-1]:.3f}"
            )

            print(
                f"  Precision@{k}: "
                f"{precision_scores[k][-1]:.3f}"
            )

            print(
                f"  HitRate@{k}: "
                f"{hit_scores[k][-1]:.3f}"
            )

            print(
            f"  Diversity@{k}: "
            f"{diversity_scores[k][-1]:.3f}"
            )
        print(
            f"  Reciprocal Rank: "
            f"{reciprocal_ranks[-1]:.3f}"
        )

        print(
            f"  Retrieval latency: "
            f"{response.retrieval_time_ms:.3f} ms"
        )

# --------------------------------------------------------
    # Aggregate report
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("DIVERSIFIED RESULTS")
    print("=" * 80)

    for k in K_VALUES:
        mean_recall = statistics.mean(recall_scores[k])
        mean_precision = statistics.mean(precision_scores[k])
        mean_hit = statistics.mean(hit_scores[k])
        mean_diversity = statistics.mean(diversity_scores[k])

        print(f"\nK = {k}")
        print(f"  Recall@{k:<2}    = {mean_recall:.4f}")
        print(f"  Precision@{k:<2} = {mean_precision:.4f}")
        print(f"  HitRate@{k:<2}   = {mean_hit:.4f}")
        print(f"  Diversity@{k:<2} = {mean_diversity:.4f}")

    mean_mrr = mean_reciprocal_rank(reciprocal_ranks)
    mean_latency = statistics.mean(retrieval_latencies) if retrieval_latencies else 0.0

    # if retrieval_latencies:
    #     sorted_latencies = sorted(retrieval_latencies)
    #     idx = max(0, int(0.95 * len(sorted_latencies)) - 1)
    #     p95_latency = sorted_latencies[idx]
    # else:
    #     p95_latency = 0.0
    if retrieval_latencies:
        p95_latency = float(
            np.percentile(
                retrieval_latencies,
                95
            )
        )
    else:
        p95_latency = 0.0

    print(f"\nMRR = {mean_mrr:.4f}")
    print(f"Mean Retrieval Latency = {mean_latency:.3f} ms")
    print(f"P95 Retrieval Latency  = {p95_latency:.3f} ms")
    print("\n" + "=" * 80)

    # --------------------------------------------------------
    # Save experiment results (.jsonl format)
    # --------------------------------------------------------

    results = {
        "experiment": "diversified_retrieval",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "embedding_model": retrieval_config.embedding_model,
        "vector_store": "FAISS",
        "configuration": {
            "chunk_size": retrieval_config.chunk_size,
            "chunk_overlap": retrieval_config.chunk_overlap,
            "candidate_k": retrieval_config.candidate_k,
            "top_k": retrieval_config.top_k,
            "metadata_filtering": retrieval_config.use_metadata_filtering,
            "reranking": retrieval_config.use_reranker,
            "diversification": retrieval_config.use_diversification,
            "max_chunks_per_document": retrieval_config.max_chunks_per_document,
        },
        "evaluation_queries": len(dataset),
        "metrics": {
            "recall_at_1": statistics.mean(recall_scores[1]),
            "recall_at_3": statistics.mean(recall_scores[3]),
            "recall_at_5": statistics.mean(recall_scores[5]),
            "precision_at_1": statistics.mean(precision_scores[1]),
            "precision_at_3": statistics.mean(precision_scores[3]),
            "precision_at_5": statistics.mean(precision_scores[5]),
            "hit_rate_at_1": statistics.mean(hit_scores[1]),
            "hit_rate_at_3": statistics.mean(hit_scores[3]),
            "hit_rate_at_5": statistics.mean(hit_scores[5]),
            "mrr": mean_mrr,
            "mean_retrieval_latency_ms": mean_latency,
            "p95_retrieval_latency_ms": p95_latency,
            "diversity_at_1": statistics.mean(diversity_scores[1]),
            "diversity_at_3": statistics.mean(diversity_scores[3]),
            "diversity_at_5": statistics.mean(diversity_scores[5]),
        },
        "notes": [
            "Document diversification enabled.",
            "Maximum one chunk per document in the first selection pass.",
            "No reranker.",
            "No query expansion.",
        ],
    }

    with RESULTS_PATH.open(
    "a",
    encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                results,
                indent=2,
            )
        )

        file.write(
            "\n" + "=" * 80 + "\n"
        )

    print(
        f"\nResults appended to:\n"
        f"{RESULTS_PATH}"
    )

if __name__ == "__main__":
    main()