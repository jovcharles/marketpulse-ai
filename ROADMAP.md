# MarketPulse AI - Roadmap

This roadmap outlines the phases of development for MarketPulse AI, evolving it from a raw data pipeline into an intelligent, AI-assisted cryptocurrency intelligence system.

---

## Phase 1: Intelligent Query Planner (Completed)

### Objective
Build an AI-powered query planner that analyzes natural language questions, extracts critical financial and temporal entities, and determines the optimal retrieval strategy (SQL, Vector, or Hybrid) without executing arbitrary or unsafe database operations.

### Key Milestones
- [x] Define `QueryPlan` schema with intent classification and source routing constraints.
- [x] Implement deterministic fast-path parser for high-confidence financial queries (tickers, dates, metrics).
- [x] Implement modular LLM provider interface for complex or ambiguous natural language queries.
- [x] Implement query planning service adhering to separation of concerns (planning decoupled from execution).
- [x] Expose `POST /query/plan` API endpoint in the FastAPI backend.
- [x] Comprehensive test suite covering intent routing, entity extraction, date normalization, and validation rules.

---

## Phase 2: Structured SQL Retrieval & Analytical Service (Completed)

### Objective
Implement secure, read-only analytical SQL query execution based on plans generated in Phase 1.

### Key Milestones
- [x] Implement `PriceRepository` for structured historical price retrieval and aggregations (OHLCV, price changes, highs/lows, moving averages).
- [x] Implement SQL query validator ensuring strict read-only access, parameterized queries, and execution timeouts.
- [x] Implement `PriceService` for business logic and statistical calculations.
- [x] Expose price retrieval endpoints in the backend.

---

## Phase 3: Semantic Vector Retrieval & News Analysis

### Objective
Enhance semantic search and integrate sentiment/news analysis with pgvector.

### Key Milestones
- [ ] Optimize pgvector indexing (IVFFlat/HNSW) for vector similarity search.
- [ ] Enhance news extraction with richer metadata and crypto sentiment tagging.
- [ ] Connect semantic retrieval results to query planning outputs.

---

## Phase 4: Hybrid Retrieval & Answer Synthesis

### Objective
Combine structured SQL data and unstructured vector search results into a unified context and synthesize grounded financial answers using an LLM.

### Key Milestones
- [ ] Implement hybrid retrieval orchestrator merging SQL records and semantic news context.
- [ ] Build answer generation prompt pipeline with grounding and citation of sources.
- [ ] Prevent financial hallucination through strict factual constraints.
- [ ] End-to-end API for user question answering (`POST /query/ask`).

---

## Phase 5: Production Readiness & User Interface

### Objective
Deploy scalable background pipelines and provide an intuitive user interface.

### Key Milestones
- [ ] Orchestrate recurring data ingestion and embedding updates via Apache Airflow.
- [ ] Build responsive web frontend for interactive querying and charting.
- [ ] Containerized deployment and monitoring.
