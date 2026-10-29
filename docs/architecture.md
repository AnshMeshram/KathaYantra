# KathaYantra Backend Architecture

> **Central Principle:**  
> *Preserve the story. Trace the source. Respect the culture. Keep the AI honest.*

---

## 1. Architectural Overview

KathaYantra is designed as a **local-first, rights-aware digital archive and exploration engine** for world folklore and urban legends across 15 target countries.

The backend is built with Python 3, FastAPI, Pydantic v2, and version-controlled JSON seed repositories, designed to integrate seamlessly with a locally running open-weight large language model (**Ollama + Gemma 2**) without relying on paid hosted LLMs, cloud databases, or third-party vector databases.

```mermaid
flowchart TD
    subgraph Data Tier
        RAW["data/raw/<br>Restricted Raw Data<br>(folk_tales_deduplicated.csv)"]
        AUDIT["data/manifests/<br>Audit Reports & Review<br>(nation_mapping_review.json)"]
        SEED["data/seed/<br>Reviewed JSON Datasets<br>(folklore/ & urban_legends/)"]
        REGISTRY["data/seed/<br>source_registry.json<br>(17 Registered Sources)"]
    end

    subgraph Backend Core
        FASTAPI["FastAPI Backend<br>(app/main.py)"]
        CONFIG["Core Config & Security<br>(app/core/config.py)"]
        SCHEMAS["Pydantic v2 Schemas<br>(StoryRecord, Country, Manifest)"]
        SERVICES["Manifest & Registry Services<br>(manifest_service.py)"]
        HEALTH["Health & Readiness API<br>(GET /api/v1/health)"]
    end

    subgraph Future Connectors
        API_CONNECTORS["Phase 2 API Connectors<br>(Wikimedia, Wikidata, LOC, Europeana)"]
    end

    subgraph Local AI Tier
        OLLAMA["Local Ollama Daemon<br>(http://127.0.0.1:11434)"]
        GEMMA["Gemma 2 Open-Weight LLM<br>(gemma2)"]
    end

    RAW --> AUDIT
    AUDIT -.-> SEED
    SEED --> SERVICES
    REGISTRY --> SERVICES
    CONFIG --> FASTAPI
    SCHEMAS --> FASTAPI
    SERVICES --> HEALTH
    HEALTH --> FASTAPI
    API_CONNECTORS -.-> SEED
    SEED --> FASTAPI
    FASTAPI -.-> OLLAMA
    OLLAMA --- GEMMA
```

---

## 2. Strict Boundary Separation

A primary architectural requirement is strict segregation between raw unreviewed data, reviewed seed collections, future API ingestions, and AI services:

### A. Raw Data Tier (`data/raw/`)
- Contains untouched, incoming data assets (e.g. `folk_tales_deduplicated.csv`).
- Protected by `.gitignore` to prevent unauthorized publication in public repositories.
- Records are classified as `needs_rights_review` and are **never** directly exposed via the public API or mixed with verified stories.

### B. Curated Seed Datasets (`data/seed/`)
- Version-controlled, human-inspectable JSON files.
- Structured by country code (`data/seed/folklore/<CODE>.json` and `data/seed/urban_legends/<CODE>.json`).
- Every story record must pass strict Pydantic schema validation, including documented sources, verified license state, cultural provenance, and rights classification.
- In Phase 1, all 30 files are initialized with documented, empty structures (`records: []`) to accurately reflect actual curated status.

### C. Future API Ingestion Tier (`app/integrations/`)
- Standardized connectors to external archives (Library of Congress, Wikimedia, Europeana, Japan Search).
- Governed by `data/seed/source_registry.json`.
- Enforces rate limits, attribution requirements, and credential segregation (e.g., API keys in `.env`).

### D. Local AI Inference Tier (Ollama + Gemma 2)
- Architecture: `Curated JSON data + approved metadata -> Retrieval Service -> FastAPI -> Ollama / Gemma 2`.
- AI outputs are strictly segregated using `content_origin: ai_generated_fiction`.
- The AI is **never** permitted to fabricate folklore sources, invent historical events, or act as an authoritative substitute for historical provenance.
- The system is completely resilient: if Ollama is offline or uninstalled, the archive browsing, search, and validation workflows function without disruption.

---

## 3. Data Flow and Ingestion Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Curator as Data Curator / Ingestion Script
    participant Raw as Raw Data Asset (CSV/API)
    participant Audit as Audit & Validation Engine
    participant Review as Review Manifest
    participant Seed as Curated Seed JSON
    participant API as FastAPI Backend

    Curator->>Raw: Ingest raw source asset
    Curator->>Audit: Run audit_folktales_csv.py
    Audit->>Review: Output missing values, duplicates, and nation mapping
    Review->>Curator: Flag records requiring cultural/rights review
    Curator->>Seed: Commit verified original summaries and citations
    Seed->>API: Load validated records into API service
    API->>Curator: GET /api/v1/health (true counts and coverage)
```

---

## 4. Key Invariants

1. **Source Provenance:** Every single story record must have at least one validated source citation with a functioning URL.
2. **Deterministic Processing:** Auditing and manifest generation scripts are deterministic, idempotent, and non-destructive.
3. **No Phantom Quotas:** Actual counts reflect strictly validated records. The target of 300 records is documented as a milestone, never faked.
4. **Cultural Integrity:** Regional, ethnic, and Indigenous traditions (e.g., Native American, Hawaiian, Celtic, Yoruba) are preserved with specific cultural attribution rather than flattened into modern national borders.
5. **Zero Cloud Dependencies:** No paid cloud APIs, external vector databases, or hosted LLM endpoints.

