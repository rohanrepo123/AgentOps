# Retrieval Experiments

## Baseline and Embedding Comparison

The retrieval benchmark uses 12 AcmeCloud evaluation queries with FAISS retrieval. Metrics include Recall@K, Precision@K, Hit Rate@K, MRR, retrieval latency, and document diversity.

### Initial Baseline

| Embedding | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency |
|---|---:|---:|---:|---:|---:|
| Hugging Face | **51.25%** | **90.00%** | **0.9167** | **16.56 ms** | **18.32 ms** |
| OpenAI text-embedding-3-large | 45.69% | 91.67% | 0.9167 | 382.64 ms | 459.70 ms |
| OpenAI text-embedding-3-small | 46.39% | 83.33% | 0.8333 | 325.84 ms | 379.74 ms |

The Hugging Face configuration was selected as the working retrieval baseline because it provided the strongest Recall@5 among the initial configurations while maintaining substantially lower latency.

## Candidate-Pool Ablation

After enabling document diversification, `candidate_k` was evaluated at 10, 15, 20, and 30.

| Embedding | Candidate K | Recall@5 | Precision@5 | Mean Latency | P95 Latency |
|---|---:|---:|---:|---:|---:|
| Hugging Face | 10 | 51.25% | 90.00% | 16.42 ms | 16.95 ms |
| Hugging Face | 15 | 57.50% | 90.00% | 14.10 ms | 15.30 ms |
| **Hugging Face** | **20** | **58.89%** | **90.00%** | **14.39 ms** | **17.56 ms** |
| Hugging Face | 30 | 58.89% | 82.78% | 16.24 ms | 21.55 ms |
| OpenAI text-embedding-3-large | 10 | 47.08% | 91.67% | 485.97 ms | 746.38 ms |
| OpenAI text-embedding-3-large | 15 | 54.72% | 87.22% | 383.31 ms | 450.87 ms |
| OpenAI text-embedding-3-large | 20 | 57.50% | 95.56% | 411.35 ms | 563.92 ms |
| **OpenAI text-embedding-3-large** | **30** | **60.28%** | **89.44%** | **357.51 ms** | **415.42 ms** |

## Findings

- For Hugging Face embeddings, `candidate_k=20` is the current operating point.
- Increasing Hugging Face `candidate_k` from 20 to 30 does not improve Recall@5 but reduces Precision@5 from 90.00% to 82.78%.
- OpenAI `text-embedding-3-large` reaches higher maximum Recall@5, but at substantially higher retrieval latency.
- The benchmark therefore favors Hugging Face embeddings with `candidate_k=20` for the current production-oriented design.

## Planned Experiments

- Metadata normalization
- Filter robustness
- Reranking
- Query expansion
- Hybrid retrieval
- Context compression
- Retrieval regression testing
