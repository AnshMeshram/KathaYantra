# KathaYantra Backend Architecture (Phase 5)

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

---

## 1. Architectural Overview

KathaYantra is designed as a **local-first, rights-aware digital archive, exploration engine, and grounded AI assistant** for world folklore and urban legends across 15 target countries.

In Phase 5, the architecture introduces **the Local AI Archivist subsystem**:
- **Ollama Client (`app/services/ollama_client.py`):** Asynchronous HTTP client communicating with a locally running Ollama instance hosting Google's open-weight `gemma2` model, with health checks, timeout resilience, and retry policies.
- **SQLite FTS5 Retrieval Engine (`app/services/retrieval_index.py`, `app/services/retrieval.py`):** Standalone full-text search index (`data/processed/retrieval/retrieval_index.db`) compiling all 300 verified stories with BM25 ranking, conversational stopword filtering, and metadata filtering.
- **Grounded Q&A Service (`app/services/question_answering.py`):** Multi-stage RAG pipeline retrieving authentic records, assembling evidence contexts, prompting Gemma 2 with strict evidence boundaries, and extracting verifiable citations directly from catalog metadata.
- **Comparative Analysis Service (`app/services/story_comparison.py`):** Cross-cultural comparison engine examining motifs, cultural contexts, regional variants, and differences without assuming false genealogical transmission.
- **Isolated Fiction Generation Service (`app/services/fiction_service.py`):** Creative storytelling engine generating synthetic narratives inspired by authentic motifs, strictly encapsulated in `GeneratedFictionRecord` models and quarantined in `data/processed/generated_fiction/`.
- **Offline Resilience:** 100% of the archive browsing, search, and validation operations function without degradation when Ollama is offline, with graceful degradation responses for AI endpoints.

```mermaid
flowchart TD
    subgraph Tier 1: Open Data Connectors & Ingestion
        HTTP["app/integrations/http_client.py<br>KathaHTTPClient (Rate-Limited, Cached, Polite UA)"]
        CONNECTORS["app/integrations/<br>Wikimedia, Wikidata, LOC, IA, Myths of Ireland, Europeana, Japan Search, CSV"]
        HTTP --> CONNECTORS
    end

    subgraph Tier 2: Staging Pipeline & Repository
        PIPELINE["app/services/import_pipeline.py<br>8-Stage Candidate Ingestion Pipeline"]
        DEDUP["app/services/candidate_deduplication.py<br>Fingerprinting & Variant Analysis"]
        REPO["app/repositories/candidate_repository.py<br>Staged Candidates (data/processed/candidates/)"]
        CONNECTORS --> PIPELINE
        PIPELINE --> DEDUP
        DEDUP --> REPO
    end

    subgraph Tier 3: Governance & Curated Seed
        POLICY["app/services/publication_policy.py<br>Deterministic Publication Policy Engine (10 Rules)"]
        SEED["data/seed/folklore/ & urban_legends/<br>30 Canonical DatasetEnvelopes (300 Verified Stories)"]
        POLICY --> SEED
    end

    subgraph Tier 4: FTS5 Retrieval & Search Engine
        COMPILER["app/services/retrieval_index.py<br>FTS5 Compiler (Zero Unverified / Zero AI)"]
        FTS_DB["data/processed/retrieval/retrieval_index.db<br>SQLite FTS5 with BM25 Ranking"]
        SEARCH["app/services/retrieval.py<br>RetrievalService (Stopword Filter & BM25 Scoring)"]
        SEED --> COMPILER
        COMPILER --> FTS_DB
        FTS_DB --> SEARCH
    end

    subgraph Tier 5: Local AI Archivist & RAG Services
        OLLAMA["app/services/ollama_client.py<br>OllamaClient (Local gemma2:latest)"]
        QA["app/services/question_answering.py<br>QuestionAnsweringService (Grounded RAG)"]
        COMPARE["app/services/story_comparison.py<br>StoryComparisonService (Comparative Analysis)"]
        FICTION["app/services/fiction_service.py<br>FictionGenerationService (Creative Synthesis)"]
        SEARCH --> QA
        SEARCH --> COMPARE
        SEARCH --> FICTION
        OLLAMA --> QA
        OLLAMA --> COMPARE
        OLLAMA --> FICTION
    end

    subgraph Tier 6: Quarantined Generated Fiction
        FIC_STORAGE["data/processed/generated_fiction/<br>GeneratedFictionRecord (Quarantined)"]
        FICTION --> FIC_STORAGE
    end
```

---

## 2. Decoupled Ingestion & Staging Pipeline

A critical Phase 2 enhancement is the formal decoupling of incomplete incoming data from published cultural records:

```mermaid
sequenceDiagram
    autonumber
    actor Curator as Ingestion Pipeline / Curator
    participant Raw as Raw Source Data (CSV / API)
    participant Staging as ImportCandidate (Staging)
    participant Policy as PublicationPolicy Service
    participant Seed as DatasetEnvelope (Curated Seed)
    participant AI as Local AI (Gemma 2)

    Curator->>Raw: Harvest or audit raw inputs
    Raw->>Staging: Ingest into ImportCandidate (new_candidate)
    Note over Staging: Incomplete fields, unverified URLs, missing country allowed in staging
    Curator->>Staging: Review rights, nation mapping, and write original summary
    Staging->>Policy: Submit candidate for publication review
    alt Passes All 8 Policy Checks
        Policy->>Seed: Promote to StoryRecord in DatasetEnvelope
    else Fails Policy (e.g. Needs Rights Review or Unverified)
        Policy-->>Curator: Return validation violations; remain in staging
    end
    AI-->>Curator: Generates creative story with mandatory disclaimer
    Note over AI: AI fiction saved strictly to GeneratedFictionRecord; rejected by StoryRecord
```

---

## 3. The 17 Data Quality Checks

The `DataQualityValidator` ([`app/services/data_validation.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\services\data_validation.py)) evaluates:

1. **JSON Syntax:** Clean JSON parsing without truncation or syntax errors.
2. **Dataset Envelope:** Proper `DatasetEnvelope` root structure (`schema_version: "2.0.0"`).
3. **Country/Category Alignment:** File `IN.json` in `folklore/` must declare `country_code: "IN"` and `category: "folklore"`.
4. **Story Schema Conformance:** Validates every record against `StoryRecord`.
5. **Stable ID Format:** Matches `^[A-Z]{2}-(FOLK|URBAN)-[0-9]{3,}$`.
6. **Global Duplicate IDs:** Zero duplicate record IDs across all 30 seed files.
7. **Recurring Titles:** Identifies duplicate titles across regions for editorial review.
8. **Source URL Validity:** Enforces valid HTTP/HTTPS schemes and network locations.
9. **Mandatory Sources:** Every story record must contain $\ge 1$ traceable source.
10. **Rights Status Presence:** Assesses explicit legal rights state.
11. **Unverified Records:** Prevents unverified records from being labeled "approved".
12. **Prefix Consistency:** Enforces that record ID prefixes match country code and category tag.
13. **AI Fiction Segregation:** Rejects any record with `content_origin: ai_generated_fiction` from seed files.
14. **Manifest Discrepancy:** Verifies that actual counts match manifest totals.
15. **Source Registry References:** Verifies citation links to `source_registry.json`.
16. **Controlled Enums:** Restricts categories, verification states, and rights to approved enums.
17. **Timestamps & Languages:** Validates ISO 8601 UTC timestamps and ISO language codes.

---

## 4. Key Archival Invariants

- **Curated Published Archive:** 300 verified stories (150 folklore + 150 urban legends, 20 per country across 15 countries) pass all 10 `PublicationPolicy` rules with 100% genuine bibliographic citations.
- **Quarantined Raw Corpus:** The 2,938-row `folk_tales_deduplicated.csv` remains strictly in `data/raw/` (gitignored).
- **Draft 2020-12 Contract Exports:** Machine-readable schemas in `data/schemas/` are regenerated automatically from Pydantic models.
- **Fail-Safe Local AI:** The entire backend and validation suite operates with 100% functionality when Ollama is offline.
- **Strict Evidence Grounding:** Factual AI responses cite only genuine records retrieved from the database; model memory hallucinations and fabricated URLs are strictly prohibited.
- **Quarantined Synthetic Fiction:** All AI-generated fiction records are segregated into `data/processed/generated_fiction/` and barred from seed files.

---

## 5. Phase 5 Local AI Archivist Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as User / API Client
    participant Router as API Route (/api/v1/ai/ask)
    participant QA as QuestionAnsweringService
    participant Search as RetrievalService (FTS5)
    participant DB as SQLite FTS5 (retrieval_index.db)
    participant Ollama as OllamaClient
    participant LLM as Local Gemma 2 (9.2B)

    User->>Router: POST /api/v1/ai/ask { query: "Tell me about Saci-Perere", country_code: "BR" }
    Router->>QA: answer_question(query, filters)
    QA->>Search: search(query="Saci-Perere", category=None, country="BR", limit=5)
    Search->>DB: MATCH 'Saci* OR Perere*' + BM25 ranking
    DB-->>Search: Top scored StoryRecords (BR-FOLK-001)
    Search-->>QA: List[RetrievalResultItem] (score >= 0.5)

    alt Insufficient Evidence Found
        QA-->>Router: AIQuestionResponse (answer_type="insufficient_evidence", confidence=0.0)
    else Sufficient Evidence Found
        QA->>QA: Build Evidence Context (ID, Title, Country, Region, Motifs, Sources)
        QA->>Ollama: POST /api/chat (system_prompt + context + user query)
        alt Ollama is Offline / Times Out
            Ollama-->>QA: OllamaConnectionError
            QA-->>Router: Graceful fallback answer + extracted citations
        else Ollama Responds
            Ollama->>LLM: Local GPU/CPU Inference
            LLM-->>Ollama: Grounded response text
            Ollama-->>QA: ChatResponse
            QA->>QA: Attach metadata citations (Title, URL, Publisher, Rights)
            QA-->>Router: AIQuestionResponse (answer_type="grounded_answer", citations)
        end
    end
    Router-->>User: JSON Response
```
