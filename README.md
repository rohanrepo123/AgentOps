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
- Added a local cross-encoder reranking experiment with controlled candidate-pool ablations.
- Added deterministic multi-query expansion with merged, deduplicated candidate retrieval and controlled ablation benchmarking.

## Retrieval Benchmark

All results use the AcmeCloud evaluation set and the same FAISS retrieval pipeline. The dense-retrieval configuration uses metadata filtering and document diversification with `candidate_k=20` and `top_k=5`.

### Candidate-Pool Ablation: Dense Retrieval

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

### Reranking Ablation

The reranking experiment keeps the retrieval pipeline fixed and varies only the FAISS candidate pool supplied to the local cross-encoder `BAAI/bge-reranker-base`. Final output remains `top_k=5`, with metadata filtering and document diversification enabled.

| Candidate K | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency | Diversity@5 |
|---:|---:|---:|---:|---:|---:|---:|
| **20** | **62.36%** | **60.00%** | **0.9583** | **~1.0 s** | **~1.51 s** | **100%** |
| 30 | 58.89% | 56.67% | 0.9583 | 1307.63 ms | 1566.33 ms | 100% |
| 50 | 57.08% | 55.00% | 0.9167 | 1863.07 ms | 2128.28 ms | 100% |
| 100 | 54.03% | 51.67% | 0.9167 | 3460.32 ms | 4025.06 ms | 100% |

#### Reranking Findings

- `candidate_k=20` is the best operating point among the tested reranking configurations.
- Increasing the reranker candidate pool from 20 to 30, 50, and 100 progressively reduced Recall@5 from **62.36% to 58.89%, 57.08%, and 54.03%**.
- Precision@5 also declined as the candidate pool increased, falling from **60.00% at K=20 to 51.67% at K=100**.
- Mean latency increased substantially as the reranker candidate pool increased, reaching roughly **3.46 s at K=100**.
- Diversity remained **100%** across the tested reranking configurations after correcting the retrieval ordering so that the reranker scores the full candidate pool before final diversification.
- Increasing reranker candidate depth therefore does not improve aggregate retrieval quality on the current AcmeCloud benchmark and introduces substantial additional inference cost.
- The current evidence favors keeping the dense retriever as the default retrieval path rather than enabling this cross-encoder reranker by default.

### Multi-Query Expansion Ablation

The multi-query experiment compares the `candidate_k=20` reranking baseline against deterministic multi-query retrieval. The multi-query path keeps the original query, generates up to three targeted variants, retrieves candidates for each query, merges and deduplicates the candidate pool, reranks the merged candidates using the original user query, and applies final document diversification.

| Configuration | Recall@5 | Precision@5 | MRR | Mean Latency | Diversity@5 | Mean Raw Candidates | Mean Unique Chunks | Mean Unique Documents |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Reranker baseline | 62.36% | 60.00% | 0.9583 | 131.83 ms | 100% | 20.00 | 20.00 | 13.17 |
| **Multi-query v2** | **64.44%** | **61.67%** | **0.9583** | **134.37 ms** | **100%** | **70.00** | **28.58** | **17.92** |

#### Multi-Query Findings

- Multi-query expansion improved Recall@5 from **62.36% to 64.44%**, a **2.08 percentage-point gain**.
- Precision@5 improved from **60.00% to 61.67%**, while MRR remained unchanged at **0.9583**.
- Hit Rate@5 remained **100%** and Diversity@5 remained **100%**.
- Mean observed retrieval latency increased only from **131.83 ms to 134.37 ms**, an increase of approximately **2.53 ms (1.9%)** in this paired benchmark run.
- Multi-query retrieval increased the average raw FAISS candidate count from **20 to 70**, while deduplication reduced the average merged candidate pool to **28.58 unique chunks**.
- The candidate expansion is query-dependent: queries without a matching expansion rule still use the original query only.
- The strongest observed improvement was on notification-queue investigation, where Recall@5 increased from **75% to 100%**.
- The result is promising but should be treated as an engineering finding rather than a general production claim because the benchmark is small and synthetic.

### Current Findings

- After metadata normalization, the Hugging Face `candidate_k=20` configuration achieved **61.67% Recall@5**, **98.33% Precision@5**, **100% Hit Rate@5**, and **1.0000 MRR** on the dense-retrieval benchmark.
- Increasing Hugging Face `candidate_k` from 10 to 15 improved Recall@5 from **51.25% to 57.50%**, with a further improvement to **61.67%** at K=20.
- Increasing dense-retrieval `candidate_k` from 20 to 30 produced no additional Recall@5, while Precision@5 dropped to **91.11%**.
- OpenAI `text-embedding-3-large` reached **60.28% Recall@5** at `candidate_k=30`, but its retrieval latency remained substantially higher than the Hugging Face configuration.
- The current dense-retrieval operating point is **Hugging Face embeddings with `candidate_k=20` and `top_k=5`**, balancing retrieval quality, precision, and latency.
- The reranking ablation shows that increasing cross-encoder candidate depth beyond 20 worsens both retrieval quality and latency on the current benchmark.
- Multi-query expansion provides a modest retrieval-quality improvement over the reranking baseline while preserving MRR, Hit Rate@5, and document diversity, with only a small observed latency increase in the current paired run.

### Retrieval Progression

| Stage | Configuration | Recall@5 | Precision@5 | MRR |
|---|---|---:|---:|---:|
| Initial HF baseline | HF embeddings, baseline retrieval | 51.25% | 90.00% | 0.9167 |
| Diversification | HF + diversification, `candidate_k=15` | 57.50% | 90.00% | 0.9167 |
| Candidate-pool tuning | HF + metadata normalization + diversification, `candidate_k=20` | **61.67%** | **98.33%** | **1.0000** |
| Reranking ablation | HF + cross-encoder, `candidate_k=20` | 62.36% | 60.00% | 0.9583 |
| Multi-query expansion | HF + multi-query retrieval + cross-encoder, `candidate_k=20` | **64.44%** | **61.67%** | **0.9583** |

> Note: metadata normalization was corrected before the latest dense-retrieval benchmark. The reranking and multi-query experiments are separate configurations and should not be interpreted as a single monotonic production-improvement sequence because they optimize different retrieval strategies.

The candidate-pool and multi-query studies are treated as engineering trade-off analyses rather than universal model rankings because the benchmark uses a small synthetic AcmeCloud evaluation set.

## Known Benchmark Limitations

- The earlier `RET-012` metadata-filtering failure was caused by inconsistent service metadata and has now been addressed through metadata normalization and related-service filtering.
- Reranking and multi-query experiments currently use a synthetic AcmeCloud benchmark, so retrieval behavior may not generalize to production incident corpora.
- Cross-encoder reranking adds substantially more inference cost than dense retrieval and should therefore be enabled only when its quality benefits justify the latency overhead.
- Multi-query expansion increases retrieval work and merged candidate-pool size, so the current implementation requires further candidate-budget and latency optimization before being treated as a universal production default.

## Planned Next Steps

- Hybrid retrieval
- Context compression
- Retrieval regression testing
- Multi-query candidate-budget and latency optimization
- Reranker model optimization or alternative lightweight reranking strategies
- Agentic incident investigation workflow
- LLM evaluation and observability
- Token and cost optimization
- Latency engineering
- Root-cause analysis and autonomous recovery
- Production infrastructure and deployment
