# KathaYantra Release Readiness Checklist (Phase 6 / Final Release)

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

Use this checklist to verify backend readiness before tagging a release, merging pull requests, or initiating frontend integration.

---

## Pre-Release Verification Steps

- [x] **1. Full Test Suite Execution**
  - Command: `python -m pytest -v`
  - Expected: 154 passing tests across 38 test suites, 0 failures, 0 errors.

- [x] **2. Seed Dataset Quality & Envelope Validation**
  - Command: `python scripts/validate_json_datasets.py`
  - Expected: 30 seed files inspected, 300 records verified, 0 errors, 0 warnings.

- [x] **3. Schema Version Consistency Check**
  - Command: `python scripts/migrate_seed_json.py --check`
  - Expected: All 30 files conform to Schema 2.0.0 without pending migrations.

- [x] **4. JSON Schema Synchronization**
  - Command: `python scripts/export_json_schemas.py`
  - Expected: All 8 Draft 2020-12 JSON Schema specifications generated in `data/schemas/`.

- [x] **5. Target Country Quota Verification**
  - Command: `python scripts/check_country_quotas.py`
  - Expected: 300 / 300 records (100.0% completion), 30 / 30 partitions met, 0 deficit.

- [x] **6. SQLite FTS5 Retrieval Index Integrity**
  - Command: `python scripts/audit_retrieval_index.py`
  - Expected: Index contains exactly 300 stories (150 folklore, 150 urban legends). Zero unverified records, zero synthetic fiction.

- [x] **7. AI Source-Readiness & Provenance Audit**
  - Command: `python scripts/audit_ai_source_readiness.py`
  - Expected: 300 records audited, 300 accepted (100.0%), 0 flagged.

- [x] **8. Security & Defensive Headers Check**
  - Verify `X-Content-Type-Options: nosniff`
  - Verify `X-Frame-Options: DENY`
  - Verify `X-XSS-Protection: 1; mode=block`
  - Verify `Referrer-Policy: strict-origin-when-cross-origin`

- [x] **9. Secrets & Sensitive Configuration Audit**
  - Verify `.env` is gitignored.
  - Verify `.env.example` contains only template placeholders.
  - Verify `GET /api/v1/sources` strips any key containing `"key"` or `"secret"`.
  - Verify unhandled exceptions do not leak stack traces or internal paths to clients.

- [x] **10. Local Ollama & Gemma 2 Probing**
  - Command: `python scripts/check_ollama.py`
  - Expected: Daemon reachable, model `gemma2` detected.

- [x] **11. Offline Fallback Verification**
  - Verify that when Ollama is offline:
    - Root `/`, health `/api/v1/health`, countries, folklore, urban legends, search, and dataset endpoints continue working with 100% functionality.
    - AI endpoints return graceful fallback with extracted citations.

- [x] **12. Git Repository Hygiene**
  - Command: `git status`
  - Expected: Clean working tree, no untracked `.env` files or scratch logs.

---

## Release Status Declaration

**Current Status:** **READY FOR RELEASE & FRONTEND CONSUMPTION**  
**Verified Milestones:** Phases 1, 2, 3, 4, 5, and 6 complete.  
**Corpus:** 300 curated stories across 15 countries with 100% genuine bibliographic provenance.
