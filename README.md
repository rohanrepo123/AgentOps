AgentOps

Production-oriented agentic AI platform for autonomous incident investigation,
LLM evaluation, retrieval optimization, latency reduction, token minimization,
and AI system observability.

Current Progress

Phase 1: Retrieval Foundation ✅

Built AcmeCloud synthetic production dataset

Added 53-document engineering knowledge base

Implemented metadata-aware document loading

Added section-aware document chunking

Integrated multiple embedding configurations

Built FAISS vector store

Implemented retrieval pipeline

Added documentation search tool

Added retrieval evaluation framework

Added Recall@K, Precision@K, Hit Rate@K and MRR

Established retrieval baselines

Integrated LangSmith tracing

Retrieval Baseline Comparison

Three embedding configurations have currently been evaluated using the same
12-query benchmark and FAISS retrieval pipeline.

Embedding Model

Recall@1

Recall@3

Recall@5

Precision@5

MRR

Mean Latency

P95 Latency

Hugging Face (baseline)

19.72%

45.69%

51.25%

90.00%

0.9167

16.56 ms

18.32 ms

OpenAI text-embedding-3-large

19.72%

38.47%

45.69%

91.67%

0.9167

382.64 ms

459.70 ms

OpenAI text-embedding-3-small

17.64%

41.53%

46.39%

83.33%

0.8333

325.84 ms

379.74 ms

Initial Observation

The current Hugging Face embedding configuration provides the strongest Recall@5
and MRR while also having substantially lower retrieval latency than the tested
OpenAI embedding configurations.

The OpenAI text-embedding-3-large configuration achieved slightly higher
Precision@5 than the Hugging Face baseline, but with substantially higher latency.

These results are treated as experimental measurements rather than final conclusions.
Future retrieval improvements will be evaluated against the frozen baseline.

Next

Planned retrieval-quality experiments:

Metadata normalization

Document diversification

Reranking

Query expansion

Hybrid retrieval

Context compression

Every optimization will be benchmarked using the same evaluation dataset and
compared against the recorded baseline results.