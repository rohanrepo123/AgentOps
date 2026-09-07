# AgentOps

Production-oriented agentic AI platform for autonomous incident investigation, LLM evaluation, retrieval optimization, latency reduction, token minimization, and AI system observability.

## Current Progress

### Phase 1: Retrieval Foundation ✅

- Built a synthetic AcmeCloud production environment for reproducible experiments.
- Added a 53-document engineering knowledge base covering architecture, services, APIs, runbooks, troubleshooting, and historical incidents.
- Implemented metadata-aware document loading and section-aware chunking.
- Integrated Hugging Face embeddings and OpenAI embedding configurations for benchmark comparison.
- Built a FAISS vector store and retrieval pipeline.
- Added metadata filtering and document diversification.
- Added a documentation search tool for the future investigation agent.
- Added a retrieval evaluation framework with Recall@K, Precision@K, Hit Rate@K, MRR, latency, and document-diversity metrics.
- Integrated LangSmith tracing.

## Retrieval Benchmark

All results below use the same 12-query AcmeCloud evaluation set and the same FAISS retrieval pipeline. The current retrieval configuration uses metadata filtering and document diversification with `top_k=5`.

### Candidate-Pool Ablation

| Embedding Model | Candidate K | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency |
|---|---:|---:|---:|---:|---:|---:|
| Hugging Face | 10 | 51.25% | 90.00% | 0.9167 | 16.42 ms | 16.95 ms |
| Hugging Face | 15 | 57.50% | 90.00% | 0.9167 | 14.10 ms | 15.30 ms |
| **Hugging Face** | **20** | **58.89%** | **90.00%** | **0.9167** | **14.39 ms** | **17.56 ms** |
| Hugging Face | 30 | 58.89% | 82.78% | 0.9167 | 16.24 ms | 21.55 ms |
| OpenAI text-embedding-3-large | 10 | 47.08% | 91.67% | 0.9167 | 485.97 ms | 746.38 ms |
| OpenAI text-embedding-3-large | 15 | 54.72% | 87.22% | 0.9167 | 383.31 ms | 450.87 ms |
| OpenAI text-embedding-3-large | 20 | 57.50% | 95.56% | 1.0000 | 411.35 ms | 563.92 ms |
| **OpenAI text-embedding-3-large** | **30** | **60.28%** | **89.44%** | **1.0000** | **357.51 ms** | **415.42 ms** |

### Current Findings

- Increasing `candidate_k` from 10 to 20 improved Hugging Face Recall@5 from **51.25% to 58.89%** without reducing Precision@5.
- Increasing Hugging Face `candidate_k` from 20 to 30 produced **no additional Recall@5**, while Precision@5 dropped from **90.00% to 82.78%** and P95 latency increased.
- OpenAI `text-embedding-3-large` reached the highest Recall@5 in this benchmark at `candidate_k=30` (**60.28%**), but retrieval latency remained substantially higher than the Hugging Face configuration.
- The current production-oriented operating point is **Hugging Face embeddings with `candidate_k=20` and `top_k=5`**, balancing retrieval quality and latency.

### Retrieval Progression

| Stage | Configuration | Recall@5 |
|---|---|---:|
| Initial HF baseline | HF embeddings, baseline retrieval | 51.25% |
| Diversification | HF + diversification, `candidate_k=15` | 57.50% |
| Candidate-pool tuning | HF + diversification, `candidate_k=20` | **58.89%** |

The candidate-pool study is treated as an engineering trade-off analysis rather than a universal embedding-model ranking because the benchmark currently contains 12 evaluation queries.

## Known Benchmark Limitation

`RET-012` currently returns no documents when the `rate-limit` service filter is applied. The expected documents include `incident-inc-010`, `incident-inc-023`, and `arch-service-architecture`. This is being preserved as a known retrieval failure so later metadata normalization and filtering improvements can be measured against the same failure case.

## Planned Next Steps

- Metadata normalization and filter robustness
- Reranking
- Query expansion
- Hybrid retrieval
- Context compression
- Retrieval regression testing
- Agentic incident investigation workflow
- LLM evaluation and observability
- Token and cost optimization
- Latency engineering
- Root-cause analysis and autonomous recovery
- Production infrastructure and deployment
