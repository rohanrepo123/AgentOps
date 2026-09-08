# Reranking Experiment

## Controlled comparison

Fixed configuration:

- Embedding model: `BAAI/bge-small-en-v1.5`
- `candidate_k = 20`
- `top_k = 5`
- metadata filtering: enabled
- diversification: enabled
- max chunks/document: `1`

Only `use_reranker` changes.

### Pipeline

```text
FAISS
  ↓
candidate_k = 20
  ↓
metadata filtering
  ↓
diversification
  ↓
cross-encoder reranker
  ↓
top_k = 5
```

## Model

`BAAI/bge-reranker-base`

This is intentionally a local cross-encoder. The experiment is not expected to reduce latency. The engineering question is whether the quality gain justifies the added latency.

## Metrics

Record:

- Recall@1/3/5
- Precision@1/3/5
- HitRate@1/3/5
- MRR
- Diversity@5
- mean latency
- P95 latency

Do not claim reranking caused any improvement outside this controlled OFF/ON comparison.

## Implementation note

The repository already pins `sentence-transformers`, so no new Python dependency is required for this stage. The reranker is local and downloads its model from Hugging Face on first use.
