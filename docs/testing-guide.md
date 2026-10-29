# KathaYantra Testing Guide & Quality Assurance

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

KathaYantra includes a test suite comprising **154 automated tests** across **38 test modules** with **100% pass rate**, designed to run completely offline without external network or GPU dependencies.

---

## 1. Quick Test Commands

### Run Full Test Suite
```powershell
python -m pytest -v
```

### Run Phase 6 REST API Route Tests
```powershell
python -m pytest tests/test_api_v1_routes.py -v
```

### Run Local AI & Archivist Tests
```powershell
python -m pytest tests/test_ai_routes.py tests/test_ai_security.py tests/test_question_answering.py tests/test_story_comparison.py tests/test_fiction_service.py -v
```

### Run Data Governance & Schema Tests
```powershell
python -m pytest tests/test_data_validation.py tests/test_publication_policy.py tests/test_story_schema_phase2.py tests/test_country_schema.py -v
```

---

## 2. Test Architecture & Directory Layout

| Test Module | Test Count | Scope & Invariants Tested |
|---|:---:|---|
| `test_api_v1_routes.py` | 12 | Public REST API endpoints: countries, folklore, urban legends, unified stories, search, suggestions, sources, and dataset quality |
| `test_ai_routes.py` | 5 | AI REST endpoints: `/ai/ask`, `/ai/compare`, `/ai/generate-story`, `/ai/health`, validation errors |
| `test_ai_security.py` | 2 | Prompt injection resilience, secret protection, offline fallback safety |
| `test_app.py` | 3 | FastAPI application lifecycle, CORS configuration, root health probe |
| `test_audit.py` | 3 | Raw CSV parsing, missing field detection, duplicate auditing |
| `test_candidate_deduplication.py` | 2 | Fingerprinting, exact duplicate suppression, cultural variant preservation |
| `test_config.py` | 3 | Pydantic BaseSettings, comma-delimited CORS parsing, directory resilience |
| `test_country_schema.py` | 5 | Canonical CountryRecord v2.0.0, ISO alpha-2 constraints, record targets |
| `test_csv_importer.py` | 3 | Quarantined CSV candidate extraction, nation review mapping, duplicate detection |
| `test_data_validation.py` | 3 | 17-point DataQualityValidator suite: duplicate IDs, missing files, manifest reconciliation |
| `test_dataset_envelope.py` | 5 | DatasetEnvelope v2.0.0, dataset_id convention, backward-compatible aliases |
| `test_europeana_integration.py` | 4 | Europeana REST API, key handling, dormant fallback, rights mapping |
| `test_fiction_service.py` | 3 | Creative fiction generation, physical segregation, disclaimer enforcement |
| `test_generated_fiction.py` | 4 | GeneratedFictionRecord AI segregation, fiction disclaimer, AI-FIC ID pattern |
| `test_import_batches.py` | 2 | Candidate repository atomic JSONL storage, manifest compilation, reporting |
| `test_import_candidate.py` | 3 | ImportCandidate staging model, disposition state machine, quarantine logic |
| `test_import_pipeline.py` | 2 | 8-stage pipeline orchestration: acquire, normalize, validate, dedup, persist |
| `test_internet_archive_integration.py`| 3 | Internet Archive Advanced Search, item metadata, public domain dates |
| `test_japan_search_integration.py` | 3 | Japan Search REST API, Japanese kanji query parsing, metadata-only flags |
| `test_json_schema_export.py` | 2 | Draft 2020-12 JSON Schema generation, $defs handling, contract synchronization |
| `test_library_of_congress_integration.py`| 3 | LOC JSON API, WAF challenge resilience, pre-1929 rights heuristics |
| `test_manifest.py` | 2 | DatasetManifest dynamic calculation, target quotas vs actual published counts |
| `test_mediawiki_integration.py` | 4 | MediaWiki REST API, summary stripping, CC BY-SA 4.0 review notes |
| `test_migration.py` | 2 | Seed migration script idempotent upgrades, --check dry run mode |
| `test_myths_of_ireland_integration.py` | 2 | Myths of Ireland dataset, separating supernatural beings from full stories |
| `test_ollama_client.py` | 7 | OllamaClient HTTP connectivity, model discovery, retries, and timeout diagnostics |
| `test_phase4_curation_and_coverage.py` | 13 | Provenance audits, anti-hallucination checks, SummaryBuilder, CurationService & 300-story integrity |
| `test_publication_policy.py` | 6 | 10-rule deterministic PublicationPolicy evaluation and gating invariants |
| `test_question_answering.py` | 4 | Grounded Q&A, evidence context formatting, metadata citation extraction, offline fallback |
| `test_retrieval.py` | 7 | SQLite FTS5 search, BM25 scoring, stopword removal, country/category filters |
| `test_retrieval_index.py` | 3 | FTS5 index compilation, atomic transactional swap, unverified/fiction exclusion |
| `test_schemas.py` | 6 | Phase 1 schema regression tests: ISO validation, category constraints, URL schemes |
| `test_source_health.py` | 4 | Connector factory mapping, ReferenceOnly scraping prohibition, HTTP 429 retry |
| `test_source_registry.py` | 4 | 17 registered sources schema conformance, honest access reporting, filtering |
| `test_source_schema_phase2.py` | 4 | StorySource v2.0.0, attribution requirements, full-text reuse flags |
| `test_story_comparison.py` | 3 | Cross-cultural story comparison, motif analysis, transmission caution |
| `test_story_schema_phase2.py` | 5 | StoryRecord v2.0.0: ID prefix matching, AI fiction rejection, length constraints |
| `test_wikidata_integration.py` | 3 | Wikidata SPARQL endpoint, QID extraction, CC0 public domain metadata |
| **Total** | **154** | **38 Test Suites (100% Pass Rate)** |

---

## 3. Dedicated Verification Scripts

In addition to pytest, KathaYantra includes 7 standalone CLI audit and verification tools:

```powershell
# 1. 17-point Data Quality and Archival Governance Inspector
python scripts/validate_json_datasets.py

# 2. Check Schema 2.0.0 migration status across all 30 files
python scripts/migrate_seed_json.py --check

# 3. Export and sync JSON Schema Draft 2020-12 specifications
python scripts/export_json_schemas.py

# 4. 15-Country target quota and deficit tracker (300/300)
python scripts/check_country_quotas.py

# 5. SQLite FTS5 index compile verification and integrity audit
python scripts/audit_retrieval_index.py

# 6. AI Source-Readiness and Provenance Audit (100% Accepted)
python scripts/audit_ai_source_readiness.py

# 7. Local Ollama and Gemma 2 diagnostic probe
python scripts/check_ollama.py
```

---

## 4. Mocking Strategy & Live Testing

### Offline Mocking
- **HTTP Connectors:** External APIs (Wikimedia, Wikidata, LOC, IA, Europeana, Japan Search) are tested using mocked responses (`unittest.mock.patch` on `httpx.AsyncClient`).
- **Ollama LLM:** AI services (`QuestionAnsweringService`, `StoryComparisonService`, `FictionGenerationService`) mock `ollama_client.chat` to execute instant deterministically graded tests without requiring GPU/VRAM or a running daemon.

### Live Testing with Local Ollama
To run live end-to-end tests against real Gemma 2:
1. Start Ollama:
   ```powershell
   ollama serve
   ```
2. Verify model availability:
   ```powershell
   python scripts/check_ollama.py
   ```
3. Send live request to FastAPI:
   ```powershell
   curl -X POST http://127.0.0.1:8000/api/v1/ai/ask `
     -H "Content-Type: application/json" `
     -d '{"query": "Who is Saci-Perere in Brazilian folklore?", "country_code": "BR"}'
   ```
