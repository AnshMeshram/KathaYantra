# KathaYantra Data Schema & Contracts Reference (Version 2.0.0)

This document provides the authoritative reference for the KathaYantra data contracts implemented in [`app/schemas/`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/schemas/).

All schemas are validated at runtime via **Pydantic v2** and exported as **JSON Schema Draft 2020-12** specifications in [`data/schemas/`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/).

---

## 1. Canonical Story Record (`StoryRecord`)

Defined in [`app/schemas/story.py`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/schemas/story.py). Represents an authentic, documented folklore narrative or modern urban legend.

| Field Name | Type | Required | Description | Constraints / Notes |
|---|---|---|---|---|
| `id` | `str` | Yes | Stable primary identifier | Pattern: `^[A-Z]{2}-(FOLK\|URBAN)-[0-9]{3,}$` |
| `schema_version` | `str` | Yes | Schema contract version | Default: `"2.0.0"` |
| `record_version` | `str` | Yes | Semantic record version | Default: `"1.0.0"` |
| `title` | `str` | Yes | Canonical title | Min length 2, max length 300 |
| `slug` | `str` | Yes | URL-safe slug | Auto-generated from `title` if empty |
| `country_code` | `str` | Yes | Target ISO 3166-1 alpha-2 code | One of the 15 supported countries |
| `category` | `CategoryEnum` | Yes | Primary archive partition | `folklore` or `urban_legend` |
| `subtype` | `str?` | No | Sub-classification | e.g. `ghost_story`, `jataka_tale`, `cryptid`, `kaidan` |
| `summary` | `str` | Yes | Original narrative synopsis | Min 10 chars, max 5,000 chars |
| `long_description` | `str?` | No | Full narrative prose | Optional; omitted in metadata-only records (max 250k) |
| `alternate_names` | `list[str]` | No | Regional or indigenous variant titles | Max 50 items |
| `language` | `str` | Yes | Primary language of this text | Default: `"en"` |
| `alternate_languages` | `list[str]` | No | Traditional telling language codes | Max 20 items |
| `motifs` | `list[str]` | No | Thompson motif index codes / tags | Max 50 items |
| `themes` | `list[str]` | No | Curatorial keywords | Max 50 items |
| `historical_period` | `str?` | No | Earliest documented era | e.g. "Edo Period", "Vedic Era" |
| `region_or_community` | `str?` | No | Cultural, ethnic, or regional group | e.g. "Navajo Nation", "Yoruba", "Kyoto" |
| `community_attributions` | `list[str]` | No | Specific sovereign indigenous nations | Max 20 items |
| `geographic_associations` | `list[str]` | No | Landmarks, cities, or haunted sites | Max 20 items |
| `variant_notes` | `str?` | No | Comparative editorial notes | |
| `related_record_ids` | `list[str]` | No | Cross-references to other record IDs | Max 50 items |
| `sources` | `list[StorySource]` | Yes | Bibliographic citations | Min 1 required; no duplicate URLs |
| `source_type` | `str` | Yes | Primary source classification | e.g. `public_domain_anthology`, `academic_archive` |
| `license` | `str` | Yes | Legal copyright or license declaration | Default: `"Rights Managed / Educational Use"` |
| `rights_status` | `RightsStatusEnum` | Yes | Rights assessment status | Default: `needs_rights_review` |
| `attribution_text` | `str?` | No | Mandatory attribution statement | Required if source mandates attribution |
| `canonical_url` | `str?` | No | Canonical link for authoritative record | Validated HTTP/HTTPS URL |
| `retrieved_at` | `datetime?` | No | Timestamp of data retrieval | |
| `verification_status` | `VerificationStatusEnum` | Yes | Curatorial review stage | `verified`, `needs_review`, `rejected` |
| `content_origin` | `ContentOriginEnum` | Yes | Content origin classification | Synthetic fiction is strictly rejected |
| `created_at` | `datetime` | Yes | Record creation timestamp | ISO 8601 UTC |
| `updated_at` | `datetime` | Yes | Record modification timestamp | ISO 8601 UTC |

---

## 2. Bibliographic Source Reference (`StorySource`)

Defined in [`app/schemas/source.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\schemas\source.py). Embedded within `StoryRecord.sources`.

| Field Name | Type | Required | Description |
|---|---|---|---|
| `id` | `str?` | No | Source registry slug or citation identifier |
| `title` | `str` | Yes | Title of source work, book, or article |
| `publisher` | `str` | Yes | Publisher, archive, or holding institution |
| `name` | `str` | Yes | Citation label (Phase 1 compatibility; synced with title/publisher) |
| `url` | `str` | Yes | Validated HTTP/HTTPS URL |
| `canonical_url` | `str?` | No | Permanent canonical URL |
| `external_id` | `str?` | No | Catalog accession ID (ISBN, LoC, OCLC) |
| `source_type` | `str` | Yes | Type: `book`, `academic`, `archive`, `web`, `api` |
| `language` | `str` | Yes | Source text language code (default: `"en"`) |
| `published_at` | `str?` | No | Publication date or historical era string |
| `license_name` | `str?` | No | Documented license (e.g. Public Domain, CC0) |
| `license_url` | `str?` | No | License URL if publicly documented |
| `rights_status` | `RightsStatusEnum` | Yes | Assessed rights classification |
| `reuse_scope` | `str` | Yes | Default: `"metadata_and_citation"` |
| `attribution_required` | `bool` | Yes | Whether explicit attribution is mandatory |
| `attribution_text` | `str?` | No | Mandatory attribution statement |
| `full_text_reuse_allowed` | `bool` | Yes | Whether full text redistribution is cleared |
| `notes` | `str?` | No | Curatorial provenance notes |
| `citation` | `str?` | No | Formal Chicago/MLA citation string |

---

## 3. Country Registry Schema (`CountryRecord`)

Defined in [`app/schemas/country.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\schemas\country.py).

| Field Name | Type | Description |
|---|---|---|
| `code` | `str` | Canonical ISO 3166-1 alpha-2 code (`IN`, `US`, `JP`, etc.) |
| `name` | `str` | Standard country name |
| `display_name` | `str` | Formal display title (e.g. "Republic of India") |
| `iso_alpha2` | `str` | Matches `code` via equality validator |
| `region` | `str` | Geographic region (e.g. South Asia, Latin America) |
| `primary_languages` | `list[str]` | Key language codes for traditional storytelling |
| `regions_or_communities` | `list[str]` | Prominent regional or cultural communities |
| `cultural_context` | `str` | Overview of folkloric and supernatural narrative traditions |
| `enabled` | `bool` | Whether country is active for ingestion |
| `record_targets` | `CountryRecordTargets` | Target quotas (`folklore: 10`, `urban_legends: 10`, `total: 20`) |
| `schema_version` | `str` | Default: `"2.0.0"` |

---

## 4. Import Candidate Staging Schema (`ImportCandidate`)

Defined in [`app/schemas/import_candidate.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\schemas\import_candidate.py). Maintains strict separation between raw incoming inputs and curated, published story records.

### Candidate Dispositions (`CandidateDispositionEnum`)
- `new_candidate`: Newly ingested raw candidate record.
- `needs_mapping_review`: Requires geographic or cultural mapping verification.
- `needs_source_verification`: Awaiting primary source traceable URL verification.
- `needs_rights_review`: Requires copyright and licensing investigation.
- `eligible_for_editorial_review`: Cleared for original summary writing.
- `approved_for_publication`: Passed editorial curation; ready for promotion to `StoryRecord`.
- `rejected`: Incompatible with project standards or duplicate.
- `duplicate_candidate`: Identified as duplicate of an existing record.

---

## 5. AI-Generated Creative Fiction Schema (`GeneratedFictionRecord`)

Defined in [`app/schemas/generated_fiction.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\schemas\generated_fiction.py).

```python
class GeneratedFictionRecord(BaseModel):
    id: str                                  # Pattern: ^AI-FIC-[0-9]{3,}$
    title: str                               # Creative story title
    content_type: Literal["ai_generated_fiction"] = "ai_generated_fiction"
    story_text: str                          # Complete generated narrative
    inspiration_story_ids: list[str] = []    # Grounded KathaYantra authentic story IDs
    inspiration_source_ids: list[str] = []   # External motif / archive references
    model_provider: str = "ollama"           # Local inference provider
    model_tag: str = "gemma2"                # Local open-weight model tag
    prompt_template_version: str = "1.0.0"   # Version of prompt harness
    generated_at: datetime                   # Generation timestamp
    fiction_disclaimer: str                  # Mandatory prominent disclosure (min 20 chars)
    verification_status: VerificationStatusEnum = VerificationStatusEnum.NEEDS_REVIEW
    record_version: str = "1.0.0"
    schema_version: str = "2.0.0"
```

> **Archival Safeguard:** The `StoryRecord` model strictly rejects any record with `content_origin: ai_generated_fiction`. AI fiction records cannot enter `data/seed/folklore/` or `data/seed/urban_legends/`.

---

## 6. Dataset Envelope Schema (`DatasetEnvelope`)

Defined in [`app/schemas/dataset.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\schemas\dataset.py). Governs all 30 country seed files:

```json
{
  "schema_version": "2.0.0",
  "dataset_id": "IN-folklore",
  "country_code": "IN",
  "category": "folklore",
  "records": [],
  "metadata": {
    "description": "Folklore archive partition for India (IN)",
    "dataset_version": "2.0.0",
    "created_at": "2026-10-29T12:00:00Z",
    "updated_at": "2026-10-29T12:00:00Z",
    "provenance_notes": "Canonical Phase 2 DatasetEnvelope schema format",
    "target_count": 10,
    "actual_record_count": 0,
    "total_records": 0,
    "status": "pending_curation",
    "validation_status": "valid",
    "last_updated": "2026-10-29T12:00:00Z",
    "import_batch_references": []
  }
}
```

---

## 7. Publication Eligibility Policy Engine

Implemented in [`app/services/publication_policy.py`](file:///C:/Users/shrin\Desktop\Hactoberfest2026\KathaYantra\app\services\publication_policy.py).

A record is publishable **only** when all 8 criteria pass:

1. **Schema Integrity:** Valid `StoryRecord` adhering to ID regex and prefix constraints.
2. **Country Code:** Must be one of the 15 supported countries.
3. **Authentic Origin:** `content_origin` must NOT be `ai_generated_fiction`.
4. **Summary Quality:** Minimum 15 characters of original narrative prose.
5. **Traceable Provenance:** At least one source with a valid HTTP/HTTPS URL.
6. **Curatorial Verification:** `verification_status` must equal `verified`.
7. **Rights Clearance:**
   - `approved` or `public_domain_verified`: Cleared for full publication.
   - `metadata_only`: Cleared for metadata only (strictly prohibits full-text payload).
   - `needs_rights_review`, `permission_required`, `restricted`, `unknown`: **BLOCKED**.
8. **Attribution:** If source specifies `attribution_required: true`, attribution text must be present.
