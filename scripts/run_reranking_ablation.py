"""
Run a controlled reranking OFF vs ON ablation.

The only intended experimental change is use_reranker.
Fixed:
  candidate_k=20
  top_k=5
  metadata filtering=True
  diversification=True
  max_chunks_per_document=1
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from time import perf_counter
from app.retrieval.config import RetrievalConfig
from app.retrieval.pipeline import RetrievalPipeline
from app.retrieval.retriever import DocumentRetriever


def reciprocal_rank(results, relevant_documents):
    for rank, result in enumerate(results, start=1):
        if result.document_id in relevant_documents:
            return 1.0 / rank
    return 0.0


def hit_at_k(results, relevant_documents):
    return float(any(r.document_id in relevant_documents for r in results))


def precision_at_k(results, relevant_documents, k):
    if not results:
        return 0.0
    return sum(r.document_id in relevant_documents for r in results[:k]) / k


def recall_at_k(results, relevant_documents, k):
    if not relevant_documents:
        return 0.0
    return sum(
        r.document_id in relevant_documents for r in results[:k]
    ) / len(relevant_documents)


def diversity_at_k(results, k):
    selected = results[:k]
    if not selected:
        return 0.0
    return len({r.document_id for r in selected}) / len(selected)


def load_cases(path: Path):
    """JSON format: [{"query": "...", "relevant_documents": ["INC-001", ...]}]."""
    return json.loads(path.read_text(encoding="utf-8"))


def run(cases, use_reranker: bool):
    # The benchmark explicitly toggles reranking at construction time.
    # All retrieval settings remain fixed at the current production baseline.
    retriever = DocumentRetriever(use_reranker=use_reranker)
    pipeline = RetrievalPipeline(retriever=retriever)

    latencies = []
    rows = []

    for case in cases:
        start = perf_counter()
        response = pipeline.retrieve(case["query"], top_k=5)
        elapsed_ms = (perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        relevant = set(case["relevant_documents"])
        results = response.results

        rows.append({
            "query": case["query"],
            "recall_at_1": recall_at_k(results, relevant, 1),
            "recall_at_3": recall_at_k(results, relevant, 3),
            "recall_at_5": recall_at_k(results, relevant, 5),
            "precision_at_1": precision_at_k(results, relevant, 1),
            "precision_at_3": precision_at_k(results, relevant, 3),
            "precision_at_5": precision_at_k(results, relevant, 5),
            "hit_at_1": hit_at_k(results[:1], relevant),
            "hit_at_3": hit_at_k(results[:3], relevant),
            "hit_at_5": hit_at_k(results[:5], relevant),
            "mrr": reciprocal_rank(results, relevant),
            "diversity_at_5": diversity_at_k(results, 5),
            "latency_ms": elapsed_ms,
            "documents": [r.document_id for r in results],
        })

    def mean(key):
        return statistics.mean(row[key] for row in rows)

    import numpy as np
    return {
        "use_reranker": use_reranker,
        "candidate_k": RetrievalConfig().candidate_k ,
        "top_k": 5,
        "mean_retrieval_latency_ms": mean("latency_ms"),
        "p95_retrieval_latency_ms": float(np.percentile(latencies, 95)),
        "recall_at_1": mean("recall_at_1"),
        "recall_at_3": mean("recall_at_3"),
        "recall_at_5": mean("recall_at_5"),
        "precision_at_1": mean("precision_at_1"),
        "precision_at_3": mean("precision_at_3"),
        "precision_at_5": mean("precision_at_5"),
        "hit_rate_at_1": mean("hit_at_1"),
        "hit_rate_at_3": mean("hit_at_3"),
        "hit_rate_at_5": mean("hit_at_5"),
        "mrr": mean("mrr"),
        "diversity_at_5": mean("diversity_at_5"),
        "per_query": rows,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("data/datasets/retrieval_eval.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/retrieval/reranking/results.json"),
    )
    args = parser.parse_args()

    cases = load_cases(args.cases)

    baseline = run(cases, use_reranker=False)
    reranked = run(cases, use_reranker=True)

    output = {
        "baseline": baseline,
        "reranked": reranked,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(output, indent=2))
