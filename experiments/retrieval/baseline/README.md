# Retrieval Experiments

| Experiment | Recall@5 | Precision@5 | MRR | P95 Latency | Status |
|---|---:|---:|---:|---:|---|
| Baseline | 51.25% | 90.00% | 0.9167 | 16.742 ms | ✅ |
| Metadata Filtering | - | - | - | - | Planned |
| Diversification | - | - | - | - | Planned |
| Reranking | - | - | - | - | Planned |
| Query Expansion | - | - | - | - | Planned |
| Hybrid Retrieval | - | - | - | - | Planned |

Hugging Face
Recall@5: 51.25%
Precision@5: 90.00%
MRR: 0.9167
Mean latency: 16.56 ms
P95: 18.32 ms

OpenAI text-embedding-3-large
Recall@5: 45.69%
Precision@5: 91.67%
MRR: 0.9167
Mean latency: 382.64 ms
P95: 459.70 ms

OpenAI text-embedding-3-small
Recall@5: 46.39%
Precision@5: 83.33%
MRR: 0.8333
Mean latency: 325.84 ms
P95: 379.74 ms