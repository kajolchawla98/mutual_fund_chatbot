# Phase-Wise Architecture: Mutual Fund Facts-Only FAQ Assistant

## 1) Solution Goal
Build a Retrieval-Augmented Generation (RAG) assistant that answers only factual mutual fund queries from official sources (AMC, AMFI, SEBI), includes exactly one citation link in every answer, and refuses advisory or opinion-based requests.

## 1.1) Strict Allowed Source URLs (No Other Scheme Pages)
Only the following scheme URLs from `problemStatement.md` are allowed for scheme-level retrieval and citations:

1. `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth`
2. `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth`
3. `https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth`
4. `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth`
5. `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth`
6. `https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth`
7. `https://groww.in/mutual-funds/motilal-oswal-small-cap-fund-direct-growth`
8. `https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth`
9. `https://groww.in/mutual-funds/icici-prudential-top-100-fund-direct-growth`
10. `https://groww.in/mutual-funds/birla-sun-life-cash-plus-direct-growth`

Notes:
- Retrieval must not cite any additional Groww scheme URL outside this list.
- AMFI/SEBI links are permitted only for educational guidance/refusal context.
- Any non-allowlisted source must be dropped by ingestion and response validator layers.

## 2) High-Level Architecture
- **Frontend UI Layer**: Groww-like themed chat widget with a "Chat with us" button, bot animation, welcome message, disclaimer, examples, and conversation history.
- **API Orchestration Layer**: Receives user query, enforces policy checks, runs retrieval, builds response, validates response format, and logs telemetry.
- **Knowledge Ingestion Layer**: Collects and normalizes data from approved public URLs and official documents (factsheets, KIM, SID, guidance pages).
- **Vector + Metadata Store**: Stores chunk embeddings and source metadata for factual retrieval.
- **Compliance Guardrail Layer**: Detects advisory queries, blocks unsafe content, and enforces strict response contract.
- **Observability Layer**: Tracks retrieval quality, refusal rate, citation validity, latency, and freshness.

## 3) Phase-Wise Implementation Plan

## Phase 0: Governance, Scope, and Guardrails
### Objective
Lock scope to facts-only behavior and define hard non-negotiable rules before development.

### Inputs
- Problem statement constraints
- Exact allowlisted scheme URLs + approved AMFI/SEBI guidance links

### Activities
- Define policy rules:
  - No investment advice, recommendations, comparisons, or return calculations.
  - No non-official sources.
  - Every answer max 3 sentences.
  - Exactly one citation link.
  - Footer format: `Last updated from sources: <date>`.
  - Only allowlisted URLs can be used in retrieval/citation.
- Define refusal taxonomy:
  - Advisory intent ("should I invest", "which fund is better")
  - Predictive/subjective requests
  - Personal portfolio questions requiring recommendation
- Define data privacy boundaries:
  - Do not collect PAN, Aadhaar, account numbers, OTP, phone, email.

### Deliverables
- Policy specification document
- Query classification matrix (factual vs refusal)

### Exit Criteria
- Policy tests approved by product and compliance stakeholders.

---

## Phase 1: Corpus Planning and Source Registry
### Objective
Create a controlled registry of approved sources for ingestion and citation.

### Inputs
- Provided 10 Groww scheme URLs (strictly fixed list)
- Official AMFI/SEBI guidance pages for educational and refusal links

### Activities
- Build source registry with fields:
  - `source_id`, `source_type`, `url`, `scheme_name`, `amc_name`, `doc_type`, `status`, `last_crawled_at`
- Hard-code URL allowlist gate:
  - Reject any scheme page URL not exactly matching the 10 provided URLs.
  - Reject third-party and aggregator sources.
- Tag source trust levels:
  - Tier 1: Allowlisted scheme URLs + their linked official docs (factsheet, KIM, SID)
  - Tier 2: AMFI/SEBI educational/guidance pages
  - Tier 3: Official statement/tax download guides
- Define freshness SLO:
  - Daily check for URL/document updates
  - Weekly full re-index

### Deliverables
- `source_registry` (JSON/DB table)
- URL allowlist and crawl policy

### Exit Criteria
- All 10 allowlisted URLs mapped, reachable, and locked in source registry.

---

## Phase 2: Data Ingestion and Normalization Pipeline
### Objective
Ingest, clean, and normalize official documents into machine-retrievable text blocks.

### Inputs
- Approved source registry

### Activities
- Build ingestion jobs:
  - HTML fetch + content extraction
  - PDF parsing (factsheets, SID, KIM)
  - Structured metadata extraction
- Normalize extracted fields:
  - Scheme name, expense ratio, exit load, minimum SIP, lock-in, benchmark, riskometer, effective date
- Chunking strategy:
  - 300-800 tokens/chunk
  - Section-aware chunking (retain heading context)
  - Overlap 50-100 tokens
- Store each chunk with metadata:
  - `source_url`, `source_title`, `doc_type`, `scheme_name`, `effective_date`, `last_updated`

### Deliverables
- ETL pipeline jobs
- Normalized document repository

### Exit Criteria
- 95%+ extraction success from approved sources; metadata completeness validated.

---

## Phase 3: Embeddings, Indexing, and Retrieval Foundation
### Objective
Enable reliable factual retrieval with strong source traceability and LLM-assisted query understanding.

### Inputs
- Clean chunked corpus

### Activities
- Generate embeddings for all chunks.
- Create hybrid retrieval:
  - Dense vector search for semantic relevance
  - Metadata filter for scheme/doc precision
  - Optional keyword BM25 fallback for exact fields
- Add LLM-assisted retrieval step using Groq fast model:
  - Query rewriting for better factual retrieval (`user query -> normalized retrieval query`)
  - Entity extraction (scheme name, metric type) before vector search
  - Retrieval-time reranking prompt over top-k chunks (no answer generation in this phase)
  - Strict grounding: model sees only retrieved chunk text + metadata
- Rank and rerank:
  - Relevance score + source quality + recency + Groq rerank score
- Retrieval output contract:
  - Top-k passages, each with source URL and timestamp

### Deliverables
- Vector index + metadata index
- Retrieval service endpoint with Groq-assisted query processor

### Exit Criteria
- Golden query benchmark achieves target recall, source precision, and citation correctness.

---

## Phase 4: Query Understanding and Safety Classification
### Objective
Classify user intent early and route to factual answering or refusal flow.

### Inputs
- User query

### Activities
- Intent classifier outputs:
  - `FACTUAL`
  - `ADVISORY_REFUSE`
  - `OUT_OF_SCOPE_REFUSE`
  - `PERFORMANCE_REDIRECT` (link to official factsheet)
- Pattern library for advisory prompts.
- Entity extraction:
  - Fund/scheme name
  - Data field requested (expense ratio, exit load, etc.)
- Sanitization:
  - Remove/ignore personal identifiers if provided by user.

### Deliverables
- Query classifier service
- Rulebook and test suite for refusal coverage

### Exit Criteria
- High precision for refusal intents; no advisory leakage in evaluation set.

---

## Phase 5: RAG Answer Generation with Strict Output Contract
### Objective
Generate concise, factual, source-backed responses under strict formatting.

### Inputs
- Query intent + retrieved passages

### Activities
- Prompt template enforces:
  - Use only retrieved facts
  - Max 3 sentences
  - Exactly one source citation URL
  - Footer with freshness date
- Response post-processor validator:
  - Sentence count checker
  - Citation count checker (must be exactly 1)
  - Date footer validator
  - Block unsupported claims
- For ambiguous retrieval:
  - Ask a clarifying factual question (no advice)
  - Or return safe fallback with official source link

### Deliverables
- Answer composer module
- Response validator middleware

### Exit Criteria
- 100% conformance to response schema in test harness.

---

## Phase 6: Refusal and Educational Redirect Flow
### Objective
Provide compliant and user-friendly refusal behavior for non-factual queries.

### Inputs
- Queries classified as advisory/non-factual

### Activities
- Use standard refusal templates:
  - Polite explanation of facts-only boundary
  - Provide one educational link (AMFI/SEBI)
- Ensure refusal responses also follow:
  - Max 3 sentences
  - Exactly one link
  - Footer date
- Capture refusal reason code for analytics.

### Deliverables
- Refusal template library
- Policy audit logs for refusals

### Exit Criteria
- All advisory test prompts refused correctly and consistently.

---

## Phase 7: Frontend Experience (Groww-Like Theme)
### Objective
Deliver a clean, familiar chat interface aligned with the problem statement.

### Inputs
- UI requirements and response API

### Activities
- Build UI components:
  - Floating `Chat with us` button
  - Bot open animation
  - Welcome text: `How can I help you today?`
  - Three sample factual questions
  - Disclaimer: `Facts-only. No investment advice.`
  - Conversation history panel
- Accessibility:
  - Keyboard navigation
  - Color contrast
  - Screen-reader labels
- Frontend validations:
  - Render one citation link clearly
  - Display footer date

### Deliverables
- Production-ready chat UI
- Session-level conversation persistence

### Exit Criteria
- UX acceptance and requirement parity with defined UI scope.

---

## Phase 8: Security, Privacy, and Compliance Controls
### Objective
Prevent sensitive data handling and enforce controlled data lifecycle.

### Inputs
- Regulatory/privacy constraints

### Activities
- Input filters to detect and redact PAN/Aadhaar/account/OTP/email/phone patterns.
- Log policy:
  - Store only minimal anonymized telemetry
  - No raw sensitive user input retention
- Security controls:
  - HTTPS everywhere
  - Secrets in vault/environment manager
  - Rate limiting and abuse protection
- Compliance evidence:
  - Source audit trails per response
  - Versioned policy rules

### Deliverables
- Privacy filter module
- Compliance checklist and audit artifacts

### Exit Criteria
- Security and privacy checks pass pre-production review.

---

## Phase 9: Testing, Evaluation, and Launch Readiness
### Objective
Validate factual correctness, policy adherence, and user experience before release.

### Inputs
- Full system build

### Activities
- Test categories:
  - Unit tests (classifier, validators, parsing)
  - Integration tests (ingestion -> retrieval -> answer)
  - Policy tests (advisory refusal, one-link rule, 3-sentence rule)
  - UI tests (chat flow, history, animation, disclaimer visibility)
- Evaluation set:
  - 100+ factual benchmark questions
  - 50+ refusal benchmark questions
- SLO targets:
  - Citation validity rate >= 99%
  - Policy adherence = 100%
  - P95 response latency within target

### Deliverables
- Test report + quality dashboard
- Launch checklist

### Exit Criteria
- All critical checks green and release approved.

---

## Phase 10: Operations, Monitoring, and Continuous Improvement
### Objective
Run the assistant reliably and keep answers fresh as source documents change.

### Inputs
- Production traffic and telemetry

### Activities
- Monitor KPIs:
  - Retrieval success
  - Refusal accuracy
  - Broken citation links
  - Freshness lag
- Set alerts:
  - Source fetch failures
  - Significant drop in answer quality
  - Policy violation detection
- Continuous improvement loop:
  - Weekly review of failed/ambiguous queries
  - Add new official sources and update taxonomy
  - Re-tune prompts and ranking

### Deliverables
- Operations runbook
- Monthly quality improvement report

### Exit Criteria
- Stable production performance and regular quality gains.

## 4) Suggested Technical Stack (Lightweight)
- **Frontend**: React/Next.js + component library for chat UX
- **Backend API**: Node.js (Express/Fastify) or Python (FastAPI)
- **Ingestion**: Python workers for scraping/parsing PDFs
- **LLM for Retrieval Assistance**: Groq fast model (query rewrite + retrieval reranking)
- **Embeddings/Retrieval**: Open-source vector DB (Qdrant/FAISS/Chroma) + metadata DB
- **Storage**: Postgres for metadata, object storage for raw docs
- **Observability**: Structured logs + metrics dashboard

## 4.1) Groq Retrieval Configuration (Reference)
- **Use in retrieval phase only**:
  - Query normalization
  - Entity extraction
  - Top-k chunk reranking
- **Do not use Groq to invent facts**:
  - Final answer must be grounded in retrieved chunks and pass response validator.
- **Environment variables**:
  - `GROQ_API_KEY`
  - `GROQ_MODEL`
  - `GROQ_BASE_URL` (optional override)

## 5) API Contracts (Reference)
- `POST /chat/query`
  - Request: `{ session_id, user_message }`
  - Response: `{ answer_text, citation_url, last_updated_date, refusal_flag }`
- `POST /ingest/run`
  - Trigger crawl/parse/index job
- `GET /health`
  - Service and dependency health status

## 6) Non-Functional Requirements
- **Reliability**: Graceful fallback for temporary source/retrieval failures.
- **Traceability**: Every answer traceable to one official source URL.
- **Performance**: Fast enough for conversational UX under expected traffic.
- **Maintainability**: Modular services with clear interfaces and test coverage.

## 7) Known Limitations (Expected)
- Answers are limited by source document freshness and availability.
- Ambiguous fund names may require user clarification.
- Performance/return-related questions cannot be directly analyzed; only official factsheet links can be shared.

## 8) Acceptance Checklist
- [ ] Facts-only responses implemented
- [ ] Advisory queries refused politely
- [ ] Max 3 sentences enforced
- [ ] Exactly one citation link enforced
- [ ] Footer date present in all responses
- [ ] Groww-like chat UI with required elements implemented
- [ ] No sensitive personal data collection
- [ ] Source auditability and monitoring enabled
