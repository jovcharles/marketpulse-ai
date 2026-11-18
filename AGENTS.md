# AGENTS.md

# MarketPulse AI - Agent Instructions

## 1. Project Overview

MarketPulse AI is an AI-powered cryptocurrency market intelligence platform that combines financial data engineering, vector search, and LLM-powered retrieval.

The system collects cryptocurrency market data, processes and stores historical price information, generates vector embeddings, and enables intelligent querying through a combination of structured SQL queries and semantic vector retrieval.

### Core Objectives

- Build a reliable cryptocurrency data ingestion pipeline.
- Store structured market data in PostgreSQL.
- Enable semantic search through pgvector.
- Integrate local LLMs for intelligent query planning.
- Support SQL, vector, and hybrid retrieval strategies.
- Maintain modular, scalable, and maintainable architecture.

---

## 2. General Development Principles

All agents must follow these principles:

1. Understand the existing architecture before modifying code.
2. Reuse existing modules, utilities, and services whenever possible.
3. Avoid unnecessary dependencies.
4. Keep implementations modular and maintainable.
5. Follow separation of concerns.
6. Avoid duplicating business logic.
7. Write type-safe and well-documented code.
8. Handle errors explicitly rather than silently ignoring them.
9. Never hardcode credentials, API keys, or environment-specific configurations.
10. Do not introduce architectural changes without a clear reason.

Prefer simple, understandable implementations over unnecessary abstractions.

## 3. Project Structure

The repository is organized into the following major components:

```text
marketpulse-ai/
├── airflow/
├── backend/
├── database/
├── frontend/
├── infra/
├── pipeline/
│   ├── extractors/
│   ├── transformers/
│   ├── loaders/
│   └── embeddings/
├── tests/
├── .env.example
├── docker-compose.yml
└── AGENTS.md
```

Respect the existing directory structure. Do not create alternative directories or duplicate existing functionality without first inspecting the project.

## 4. Technology Stack

### Data Engineering
- Python
- yfinance
- PostgreSQL
- psycopg
- Apache Airflow

### Vector Search and AI
- pgvector
- Sentence Transformers
- all-MiniLM-L6-v2
- Local LLM integration

### Infrastructure
- Docker
- Docker Compose
- PostgreSQL

### Backend and Frontend
Inspect the existing implementation before selecting frameworks, libraries, or introducing new dependencies.

Do not assume that a particular framework is being used unless it is present in the repository.

---

## 5. Data Pipeline Guidelines

The pipeline is responsible for extracting, transforming, and loading cryptocurrency market data.

### Extractors

- Keep external data retrieval logic inside `pipeline/extractors/`.
- Handle API failures and missing data.
- Avoid coupling extraction logic with database operations.
- Preserve the original source data where appropriate.

### Transformers

- Keep data transformation logic inside `pipeline/transformers/`.
- Validate incoming records before processing.
- Handle missing, invalid, and inconsistent price data.
- Keep transformations deterministic whenever possible.
- Avoid performing database operations inside transformers.

### Loaders

- Keep database persistence logic inside `pipeline/loaders/`.
- Use parameterized SQL queries.
- Avoid duplicate records through appropriate conflict-handling strategies.
- Use transactions where multiple related database operations are required.

### Embeddings

- Keep embedding generation logic inside `pipeline/embeddings/`.
- Reuse initialized embedding models instead of repeatedly loading them.
- Ensure embedding dimensions match the PostgreSQL vector column.
- Keep embedding generation separate from database persistence.
- Avoid generating duplicate embeddings unnecessarily.

---

## 6. Database Guidelines

PostgreSQL is the primary database, with pgvector supporting semantic search.

Rules:

- Use PostgreSQL-compatible SQL.
- Use parameterized queries through psycopg.
- Maintain consistent naming conventions.
- Define appropriate indexes for frequently queried columns.
- Use vector indexes when justified by query patterns and dataset size.
- Avoid unnecessary database round trips.
- Keep schema changes explicit and documented.
- Preserve data integrity through constraints and transactions.

Do not introduce SQLAlchemy unless explicitly required by an architectural decision.

---

## 7. AI and Query Planning

The AI component is responsible for determining how user questions should be answered.

The query planner should determine whether a question requires:

1. SQL retrieval — for structured financial data and numerical queries.
2. Vector retrieval — for semantic search and contextual information.
3. Hybrid retrieval — when both structured and semantic information are necessary.

### Query Planner Rules

- Separate query planning from query execution.
- Do not allow the LLM to execute arbitrary SQL.
- Validate generated SQL before execution.
- Use read-only database access for analytical queries.
- Apply query limits and execution timeouts.
- Prefer deterministic logic when LLM reasoning is unnecessary.
- Handle ambiguous user questions gracefully.
- Keep the system modular so the LLM provider can be changed without rewriting the query execution layer.

The LLM should decide the retrieval strategy, not replace the underlying data and retrieval infrastructure.

### Entity Extraction Guidelines

- Prioritize longer and multi-word aliases (e.g., "binance coin" before "bnb") to avoid false substring matching.
- Preserve the natural left-to-right appearance order of extracted entities from the user prompt.
- Use strict word boundaries (`\b`) to prevent substring collisions (e.g., avoid matching "sol" inside "consolidate" or "eth" inside "method").

---

## 8. Backend Guidelines

- Keep API endpoints focused on HTTP request handling.
- Move business logic into appropriate services.
- Separate database access from API controllers.
- Validate incoming requests.
- Use consistent response structures.
- Handle exceptions appropriately.
- Avoid exposing internal implementation details.
- Never expose secrets or sensitive configuration values.

Follow the backend's existing architectural conventions.

---

## 9. Testing Guidelines

Testing is required for new functionality and bug fixes.

Use pytest for Python testing.

Prioritize tests for:

- Data extraction.
- Data transformation.
- Invalid and missing price handling.
- Database loading.
- Embedding generation.
- Query planning.
- SQL validation.
- Vector retrieval.
- API behavior.

Run relevant tests after modifying existing functionality.

Do not remove or weaken existing tests simply to make a new implementation pass.

### Python 3.14 & Windows Testing Considerations

- When testing FastAPI endpoints on Python 3.14, test route controller functions, schemas, and services directly (or using isolated unit mocks) to avoid Starlette `TestClient` / AnyIO blocking portal deadlocks.
- Always set `PYTHONPATH="."` when executing tests via CLI.
- Keep tests isolated from live external databases or services unless explicitly running end-to-end integration suites.

---

## 10. Environment and Configuration

- Use environment variables for configuration.
- Keep credentials in `.env`.
- Maintain `.env.example` with placeholder values.
- Never commit `.env`, virtual environments, caches, or generated artifacts.
- Do not hardcode database connection strings.
- Keep development and production configurations separate.

Never overwrite user-specific environment configurations.

---

## 11. Git and Code Changes

Before modifying files:

1. Inspect the existing implementation.
2. Understand the dependencies and affected components.
3. Identify potential side effects.
4. Follow existing conventions.

When implementing changes:

- Keep changes scoped to the requested functionality.
- Avoid unrelated refactoring.
- Do not overwrite existing work.
- Do not remove functionality without explicit approval.
- Update documentation when architecture or behavior changes.

Use descriptive commit messages following conventional commit conventions where appropriate.

Examples:

- `feat(pipeline): add historical market data ingestion`
- `feat(ai): implement hybrid query planning`
- `fix(embeddings): prevent duplicate vector generation`
- `refactor(backend): separate retrieval services`
- `test(pipeline): add price transformation tests`

---

## 12. Instructions for AI Agents

When assigned a task:

1. Inspect the relevant files before proposing changes.
2. Read existing documentation and configuration.
3. Understand how the requested feature fits into the architecture.
4. Explain the proposed approach when the task involves significant architectural changes.
5. Implement the smallest maintainable solution.
6. Run relevant tests.
7. Report the files modified and explain important implementation decisions.
8. Mention any remaining issues or untested behavior.

### Important Restrictions

- For major feature requests or roadmap phases, first inspect the codebase, identify reusable components, and present an implementation plan for user approval before modifying files.
- Do not invent existing functionality.
- Do not assume a file, class, function, or database table exists without checking.
- Do not introduce unnecessary frameworks or dependencies.
- Do not replace existing implementations without understanding their purpose.
- Do not execute destructive database operations without explicit approval.
- Do not expose credentials or sensitive information.

**Primary Rule:** Preserve the existing architecture, prioritize correctness and maintainability, and make every change with a clear understanding of its impact on the overall system.