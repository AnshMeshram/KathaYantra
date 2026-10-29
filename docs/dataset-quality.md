# KathaYantra Dataset Quality, Governance & Provenance Specification

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

This document provides the canonical quality and governance specification for the KathaYantra archive, detailing data standards, publication eligibility, integrity auditing, and source provenance.

---

## 1. Archive Scope & Coverage Targets

KathaYantra archives folklore narratives and modern urban legends across **15 target countries**, with a quota target of:
- **10 folklore records** per country
- **10 urban-legend records** per country
- **300 total verified records** across 30 partitions

### Current Target vs. Actual Quota Matrix

| ISO Code | Country | Target Folklore | Actual Folklore | Target Urban | Actual Urban | Total Target | Total Actual | Status |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `IN` | India | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `US` | United States | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `JP` | Japan | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `MX` | Mexico | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `IE` | Ireland | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `GB` | United Kingdom | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `BR` | Brazil | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `GR` | Greece | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `CN` | China | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `NG` | Nigeria | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `KR` | South Korea | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `PH` | Philippines | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `ID` | Indonesia | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `EG` | Egypt | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| `DE` | Germany | 10 | 10 | 10 | 10 | 20 | 20 | **100% MET** |
| **Total** | **15 Countries** | **150** | **150** | **150** | **150** | **300** | **300** | **100.0% MET** |

---

## 2. The 10 Publication Policy Eligibility Gates

Implemented deterministically in [`app/services/publication_policy.py`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/services/publication_policy.py). A record is publishable **only** when all 10 gates pass:

1. **Schema Conformance:** Strictly adheres to Pydantic `StoryRecord` v2.0.0.
2. **Deterministic Identifier Pattern:** ID matches `^[A-Z]{2}-(FOLK|URBAN)-[0-9]{3,}$`, and the prefix matches both the country code and category tag (e.g. `IN-FOLK-001`).
3. **Supported Country Membership:** Country code must belong to the 15 supported national archives.
4. **Authentic Content Origin:** Synthetic fiction (`ai_generated_fiction`) is strictly prohibited. Only authentic origins (`licensed_dataset`, `public_domain_source`, `original_summary`, `community_contribution`, `verified_archive`) are permitted.
5. **Substantive Summary:** Narrative synopsis must be substantive, culturally informative, and $\ge 30$ characters.
6. **Traceable Source Provenance:** $\ge 1$ verified bibliographic source with valid HTTP/HTTPS URL.
7. **Curatorial Editorial Verification:** Verification status must be explicitly `verified`.
8. **Rights Clearance & Attribution:** Rights status must be `approved`, `public_domain_verified`, or `metadata_only`. If attribution is legally required, non-empty `attribution_text` must be present.
9. **Title & Summary Uniqueness:** Zero collision with duplicate or unverified records.
10. **Cultural Attribution Completeness:** Specific regional, indigenous nation, or cultural community attribution must be present.

---

## 3. The 17 Data Quality Checks

Evaluated across all 30 seed files by [`app/services/data_validation.py`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/services/data_validation.py):

1. **JSON Syntax:** Well-formed UTF-8 JSON without truncation or malformed escapes.
2. **Dataset Envelope Structure:** Valid `DatasetEnvelope` root envelope (`schema_version: "2.0.0"`).
3. **Country / Category Alignment:** Seed file `IN.json` in `folklore/` must declare `country_code: "IN"` and `category: "folklore"`.
4. **Story Schema Conformance:** Every embedded record validates against `StoryRecord`.
5. **Stable ID Regex:** Matches `^[A-Z]{2}-(FOLK|URBAN)-[0-9]{3,}$`.
6. **Global Duplicate IDs:** Zero duplicate record IDs across all 30 files.
7. **Recurring Titles:** Detection and auditing of shared titles across regions.
8. **Source URL Validity:** Enforces valid HTTP/HTTPS schemes and valid network hosts.
9. **Mandatory Sources:** Every story record contains $\ge 1$ traceable source.
10. **Rights Status Presence:** Assesses explicit legal rights state.
11. **Unverified Records Exclusion:** Prevents unverified records from being labeled "approved".
12. **Prefix Consistency:** Enforces that record ID prefixes match country code and category tag.
13. **AI Fiction Segregation:** Rejects any record with `content_origin: ai_generated_fiction` from seed files.
14. **Manifest Discrepancy:** Verifies that actual counts match manifest totals.
15. **Source Registry References:** Verifies citation links to `source_registry.json`.
16. **Controlled Enums:** Restricts categories, verification states, and rights to approved enums.
17. **Timestamps & Languages:** Validates ISO 8601 UTC timestamps and ISO language codes.

---

## 4. SQLite FTS5 Retrieval Index Compilation Integrity

Compiled by [`app/services/retrieval_index.py`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/services/retrieval_index.py):
- **Index File:** `data/processed/retrieval/retrieval_index.db`
- **Indexed Story Records:** Exactly 300 records (150 folklore, 150 urban legends, 20 per country across 15 countries).
- **Exclusion Filters:**
  - AI-generated fiction records (`ai_generated_fiction`) are strictly excluded.
  - Unverified candidates (`needs_review`, `rejected`) are strictly excluded.
  - Records failing `PublicationPolicy` are strictly excluded.
- **Atomic Build:** Rebuilds are compiled into temporary databases before atomic filesystem replacement to guarantee zero downtime.

---

## 5. Verification Commands

```powershell
python scripts/validate_json_datasets.py
python scripts/check_country_quotas.py
python scripts/audit_retrieval_index.py
python scripts/audit_ai_source_readiness.py
```
*Current result: 300 / 300 records verified, 0 errors, 0 warnings, 100% acceptance.*
