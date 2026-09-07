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

All results below use the same 12-query AcmeCloud evaluation set and the same FAISS retrieval pipeline. The current retrieval configuration uses metadata filtering and document diversification with `candidate_k=20` and `top_k=5`.

### Candidate-Pool Ablation

| Embedding Model | Candidate K | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency |
|---|---:|---:|---:|---:|---:|---:|
| Hugging Face | 10 | 51.25% | 90.00% | 0.9167 | 16.42 ms | 16.95 ms |
| Hugging Face | 15 | 57.50% | 90.00% | 0.9167 | 14.10 ms | 15.30 ms |
| **Hugging Face** | **20** | **61.67%** | **98.33%** | **1.0000** | **16.15 ms** | **25.58 ms** |
| Hugging Face | 30 | 61.67% | 91.11% | 1.0000 | 16.21 ms | 21.27 ms |
| OpenAI text-embedding-3-large | 10 | 47.08% | 91.67% | 0.9167 | 485.97 ms | 746.38 ms |
| OpenAI text-embedding-3-large | 15 | 54.72% | 87.22% | 0.9167 | 383.31 ms | 450.87 ms |
| OpenAI text-embedding-3-large | 20 | 57.50% | 95.56% | 1.0000 | 411.35 ms | 563.92 ms |
| **OpenAI text-embedding-3-large** | **30** | **60.28%** | **89.44%** | **1.0000** | **357.51 ms** | **415.42 ms** |

### Current Findings

- After metadata normalization, the Hugging Face `candidate_k=20` configuration achieved **61.67% Recall@5**, **98.33% Precision@5**, **100% Hit Rate@5**, and **1.0000 MRR** on the 12-query benchmark.
- Increasing Hugging Face `candidate_k` from 10 to 15 improved Recall@5 from **51.25% to 57.50%**.
- Increasing `candidate_k` from 15 to 20 produced a further Recall@5 improvement to **61.67%** while maintaining **98.33% Precision@5**.
- Increasing `candidate_k` from 20 to 30 produced **no additional Recall@5**, while Precision@5 dropped to **91.11%**. Therefore, `candidate_k=30` is not the preferred operating point.
- OpenAI `text-embedding-3-large` reached **60.28% Recall@5** at `candidate_k=30`, but its retrieval latency remained substantially higher than the Hugging Face configuration.
- The current production-oriented operating point is **Hugging Face embeddings with `candidate_k=20` and `top_k=5`**, balancing retrieval quality, precision, and latency.
- The latest validated latency measurement for the selected configuration is **16.15 ms mean retrieval latency** and **25.58 ms P95 latency**.

### Retrieval Progression

| Stage | Configuration | Recall@5 | Precision@5 | MRR |
|---|---|---:|---:|---:|
| Initial HF baseline | HF embeddings, baseline retrieval | 51.25% | 90.00% | 0.9167 |
| Diversification | HF + diversification, `candidate_k=15` | 57.50% | 90.00% | 0.9167 |
| Candidate-pool tuning | HF + metadata normalization + diversification, `candidate_k=20` | **61.67%** | **98.33%** | **1.0000** |

> Note: metadata normalization was also corrected before the latest candidate-pool benchmark. Therefore, the full improvement from the original baseline to the current result should not be attributed solely to increasing `candidate_k`.

The candidate-pool study is treated as an engineering trade-off analysis rather than a universal embedding-model ranking because the benchmark currently contains 12 evaluation queries.

## Known Benchmark Limitation

The earlier `RET-012` metadata-filtering failure was caused by inconsistent service metadata and has now been addressed through metadata normalization and related-service filtering. The benchmark is being kept reproducible so this class of retrieval failure can be regression-tested.

## Planned Next Steps

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
