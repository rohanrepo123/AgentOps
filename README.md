# AgentOps

Production-oriented agentic AI platform for autonomous incident investigation, LLM evaluation, retrieval optimization, latency reduction, token minimization, and AI system observability.

---

## Overview

AgentOps automates end-to-end incident root cause analysis (RCA) by orchestrating deterministic observability tools via typed LangGraph workflows. The platform pairs an evaluated retrieval foundation over production runbooks with hypothesis-driven multi-agent orchestration, isolating failures across logs, metrics, deployments, and databases while enforcing strict analytical boundaries.

```
                  +----------------------------------------------+
                  |         FastAPI Gateway / Entrypoint         |
                  +----------------------------------------------+
                                         |
                                         v
               +----------------------------------------------------+
               |          LangGraph Investigation Runtime           |
               |                                                    |
               |   [Planner] <----------------------------------+   |
               |       |                                        |   |
               |       v                                        |   |
               |   [Investigation Tools Execution]              |   |
               |       |                                        |   |
               |       v                                        |   |
               |   [Evidence Collection & Normalization]        |   |
               |       |                                        |   |
               |       v                                        |   |
               |   [Hypothesis Agent (Update & Weight)] --------+   |
               |       |                                            |
               |       v (Evidence Sufficient)                      |
               |   [Root Cause Formulation]                         |
               |       |                                            |
               |       v                                            |
               |   [Mitigation & Recommendation Engine]             |
               +----------------------------------------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |         Structured Investigation Report      |
                  +----------------------------------------------+
```

---

## Architectural Pillars

### 1. Hybrid RAG & Retrieval Engine
* **Vector Store:** Section-aware chunked FAISS vector store over AcmeCloud infrastructure, runbooks, architectures, and incident histories.
* **Embeddings:** High-throughput Hugging Face embeddings bench-tested against OpenAI `text-embedding-3-large`.
* **Reranking & Expansion:** Integrated cross-encoder reranking (`BAAI/bge-reranker-base`) and deterministic multi-query expansion pipelines with strict diversity constraints.
* **Observability:** Native LangSmith tracing across embedding, candidate generation, deduplication, and ranking stages.

### 2. Hypothesis-Driven Agent Loop
* **Deterministic Guardrails:** Tools execute against read-only interfaces. The SQLite database tool enforces entity allowlisting, parameter validation, and result ceilings; arbitrary SQL and ground-truth metadata are stripped from the agent runtime.
* **State Machine:** LangGraph-managed typed investigation state tracking tool calls, collected evidence, working hypotheses, contradictions, and confidence scores.
* **Analytical Tools:**
  * `search_documentation`: FAISS hybrid search over runbooks and postmortems.
  * `search_logs`: Structured log parsing via service, timestamp, level, trace ID, and event masks.
  * `query_metrics`: Aggregations (`avg`, `p95`, `min`, `max`, `sum`) for CPU, memory, error rates, queue depth, and retry rates.
  * `query_database`: Read-only entity-constrained inspections for core domain objects.
  * `check_service_health`: Introspection of deploy versions, health checks, timeouts, and active feature flags.

---

## Retrieval Benchmarks

All evaluations are executed against the synthetic AcmeCloud 53-document benchmark set. Dense baseline: `candidate_k=20`, `top_k=5`, metadata filtering and document diversification enabled.

### Dense Candidate-Pool Ablation

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

### Cross-Encoder Reranking Ablation (`BAAI/bge-reranker-base`)

| Candidate K | Recall@5 | Precision@5 | MRR | Mean Latency | P95 Latency | Diversity@5 |
|---:|---:|---:|---:|---:|---:|---:|
| **20** | **62.36%** | **60.00%** | **0.9583** | **~1.00 s** | **~1.51 s** | **100%** |
| 30 | 58.89% | 56.67% | 0.9583 | 1307.63 ms | 1566.33 ms | 100% |
| 50 | 57.08% | 55.00% | 0.9167 | 1863.07 ms | 2128.28 ms | 100% |
| 100 | 54.03% | 51.67% | 0.9167 | 3460.32 ms | 4025.06 ms | 100% |

### Multi-Query Expansion Ablation

| Configuration | Recall@5 | Precision@5 | MRR | Latency | Diversity@5 | Raw Candidates | Unique Chunks |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline Reranker (K=20) | 62.36% | 60.00% | 0.9583 | 131.83 ms | 100% | 20.00 | 20.00 |
| **Multi-query v2** | **64.44%** | **61.67%** | **0.9583** | **134.37 ms** | **100%** | **70.00** | **28.58** |

### Pipeline Architecture Decisions
* **Default Dense Retrieval:** Local Hugging Face embeddings at `candidate_k=20` provide optimal throughput (16.15 ms mean latency) and ranking performance (1.0000 MRR, 98.33% Precision@5).
* **Reranking Overhead:** Candidate pools exceeding K=20 degrade precision and amplify tail latency without recall gains.
* **Controlled Query Expansion:** Multi-query expansion provides a +2.08% Recall@5 gain at negligible compute cost (+2.53 ms), operating as an optional pipeline flag for high-ambiguity prompts.

---

## Investigation Workflow & Graph State

The agent transitions from naive tool execution to cyclical, hypothesis-driven verification:

```
[Incident Ingestion]
        |
        v
+---------------+       Unresolved Hypotheses
| Plan / Select | <--------------------------------+
+---------------+                                  |
        |                                          |
        v                                          |
+---------------+                                  |
| Execute Tool  |                                  |
+---------------+                                  |
        |                                          |
        v                                          |
+---------------+        +------------------+      |
| Add Evidence  | -----> | Hypothesis Agent | -----+
+---------------+        +------------------+
                                 |
                                 v Evidence Confirmed
                         +------------------+
                         | Root Cause Agent |
                         +------------------+
                                 |
                                 v
                         +------------------+
                         |  Recommendation  |
                         +------------------+
```

### Typed State Schema (`InvestigationState`)

```python
class InvestigationState(TypedDict):
    incident: str
    service: str
    severity: str
    evidence: list[EvidenceItem]
    hypotheses: list[Hypothesis]
    tool_calls: list[ToolCallRecord]
    investigation_steps: int
    max_steps: int
    status: Literal["active", "escalated", "resolved"]
    evidence_sufficient: bool
    root_cause: str | None
    root_cause_confidence: float | None
    recommendations: list[str]
    next_action: str | None
    next_action_args: dict[str, Any]
    planner_reason: str | None
    investigation_complete: bool
```

---

## Roadmap

| Phase | Milestone | Status | Details |
|---|---|:---:|---|
| **0** | Environment Setup | ✅ | Synthetic AcmeCloud environment, mock infrastructure |
| **1** | Retrieval Foundation | ✅ | FAISS index, section-aware chunking, dense/rerank ablations |
| **1** | Investigation Agent MVP | 🚧 | LangGraph runtime, typed planning state, mock tool dispatch |
| **2** | Observability & Eval | ⏳ | Comprehensive LangSmith traces, agent trajectory scoring |
| **3** | Token/Cost Optimization | ⏳ | Context window pruning, dynamic payload compression |
| **4** | Latency Engineering | ⏳ | Parallel tool execution, speculative decoding, pipeline streaming |
| **5** | Incident Detection + RCA | ⏳ | Anomaly detection alerts directly triggering graph workers |
| **6** | Autonomous Optimization | ⏳ | Self-correcting retrieval parameters and dynamic routing |
| **7** | Production Infrastructure | ⏳ | Asynchronous task queues (Celery/Redis), enterprise auth, rate limits |
| **8** | Benchmark + Deployment | ⏳ | Public real-world benchmark harness, multi-tenant deployment |

---

## Repository Structure

```text
.
├── benchmarks/              # Ablation harness and retrieval evaluation suites
├── docs/                    # Architecture RFCs and domain context
├── knowledge_base/          # AcmeCloud 53-document synthetic runbook corpus
├── src/
│   ├── agent/               # LangGraph nodes, state machines, and supervisor logic
│   ├── api/                 # FastAPI routes, schemas, and dependencies
│   ├── evaluation/          # Precision/Recall/MRR evaluation utilities
│   ├── retrieval/           # FAISS indexer, splitters, cross-encoders, multi-query
│   └── tools/               # Guarded database, log, metric, and service health interfaces
├── pyproject.toml
└── README.md
```

---

## Getting Started

### Prerequisites
* Python 3.11+
* SQLite3
* (Optional) Hugging Face API token / OpenAI API key for external benchmark runs

### Installation

```bash
git clone https://github.com/your-org/agentops.git
cd agentops

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Environment Configuration

```bash
cp .env.example .env

# Configure core runtime variables
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
OPENAI_API_KEY=your_openai_key  # Optional for OpenAI evaluations
```

### Running Retrieval Benchmarks

```bash
python benchmarks/run_retrieval_ablations.py --config configs/dense_candidate_ablation.yaml
```

### Running the Investigation Service

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
