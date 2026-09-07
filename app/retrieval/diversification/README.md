# Retrieval Diversification and Candidate-Pool Experiments

## Objective

Measure whether increasing the initial retrieval candidate pool improves final top-k retrieval quality when document diversification is enabled.

## Experimental Setup

- Evaluation set: 12 AcmeCloud retrieval queries
- Vector store: FAISS
- Final `top_k`: 5
- Metadata filtering: enabled
- Document diversification: enabled
- Maximum one chunk per document during the first selection pass
- Reranking: disabled
- Query expansion: disabled
- Candidate pool: 10, 15, 20, 30

## Results

### Hugging Face Embeddings

| Candidate K | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency | Diversity@5 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 19.72% | 48.47% | 51.25% | 90.00% | 0.9167 | 16.42 ms | 16.95 ms | 72.92% |
| 15 | 19.72% | 50.56% | 57.50% | 90.00% | 0.9167 | 14.10 ms | 15.30 ms | 70.42% |
| **20** | 19.72% | 50.56% | **58.89%** | **90.00%** | 0.9167 | **14.39 ms** | 17.56 ms | 71.25% |
| 30 | 19.72% | 50.56% | 58.89% | 82.78% | 0.9167 | 16.24 ms | 21.55 ms | 72.22% |

### OpenAI text-embedding-3-large

| Candidate K | Recall@1 | Recall@3 | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency | Diversity@5 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 19.72% | 45.69% | 47.08% | 91.67% | 0.9167 | 485.97 ms | 746.38 ms | 66.81% |
| 15 | 19.72% | 47.78% | 54.72% | 87.22% | 0.9167 | 383.31 ms | 450.87 ms | 73.33% |
| 20 | 22.50% | 50.56% | 57.50% | **95.56%** | **1.0000** | 411.35 ms | 563.92 ms | **81.67%** |
| **30** | **22.50%** | **53.33%** | **60.28%** | 89.44% | **1.0000** | **357.51 ms** | **415.42 ms** | 79.03% |

## Interpretation

### Hugging Face

`candidate_k=20` is the best current operating point. Recall@5 reaches 58.89% while Precision@5 remains 90.00%. Increasing the candidate pool to 30 provides no additional recall and causes a measurable precision and P95 latency penalty.

### OpenAI text-embedding-3-large

`candidate_k=30` produces the highest Recall@5 at 60.28%, but `candidate_k=20` provides higher Precision@5 (95.56%) and diversity. Both configurations are substantially slower than the Hugging Face setup in this benchmark.

## Current Decision

Use **Hugging Face embeddings with `candidate_k=20` and `top_k=5`** as the working retrieval configuration for subsequent AgentOps development.

The 12-query benchmark is intentionally treated as an engineering benchmark rather than a statistically general claim about embedding models.
