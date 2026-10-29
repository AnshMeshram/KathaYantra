# KathaYantra Backend Architecture (Phase 3)

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

---

## 1. Architectural Overview

KathaYantra is designed as a **local-first, rights-aware digital archive and exploration engine** for world folklore and urban legends across 15 target countries.

In Phase 3, the architecture introduces **real open-data API connectors, an asynchronous polite HTTP client with rate-limiting and caching, an 8-stage candidate ingestion pipeline, deterministic deduplication and cultural variant analysis, and candidate batch storage in `data/processed/candidates/`**.

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

    subgraph Tier 3: Governance & Publication Gate
        POLICY["app/services/publication_policy.py<br>Deterministic Publication Policy Engine (8 Rules)"]
        VALIDATOR["app/services/data_validation.py<br>DataQualityValidator (17 Checks)"]
        REPO -.-> POLICY
        POLICY --> VALIDATOR
    end

    subgraph Tier 4: Curated Seed Repositories
        SEED["data/seed/folklore/ & urban_legends/<br>30 Canonical DatasetEnvelopes (2.0.0)"]
        REGISTRY["data/seed/source_registry.json<br>17 External Repositories & APIs"]
        COUNTRIES["data/seed/countries.json<br>15 Country Canonical Records"]
        VALIDATOR --> SEED
    end

    subgraph Tier 5: Schemas & Contracts
        PYDANTIC["app/schemas/<br>Pydantic v2 Canonical Models"]
        EXPORTS["data/schemas/<br>8 JSON Schema Draft 2020-12 Documents"]
        PYDANTIC --> EXPORTS
    end

    subgraph Tier 6: Local AI & Exploration
        OLLAMA["Local Ollama Daemon<br>(http://127.0.0.1:11434)"]
        GEMMA["Gemma 2 Open-Weight LLM"]
        FICTION["app/schemas/generated_fiction.py<br>GeneratedFictionRecord (Segregated)"]
        SEED -.-> OLLAMA
        OLLAMA --- GEMMA
        GEMMA -.-> FICTION
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

- **Zero Fabricated Records:** The actual published story count remains **0** in Phase 2 until records pass human curatorial review.
- **Quarantined Raw Corpus:** The 2,938-row `folk_tales_deduplicated.csv` remains strictly in `data/raw/` (gitignored).
- **Draft 2020-12 Contract Exports:** Machine-readable schemas in `data/schemas/` are regenerated automatically from Pydantic models.
- **Fail-Safe Local AI:** The entire backend and validation suite operates with 100% functionality when Ollama is offline.
