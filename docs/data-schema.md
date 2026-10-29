# KathaYantra Data Schema Reference

This document provides the authoritative reference for the KathaYantra data models implemented in [`app/schemas/`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/app/schemas/).

All schemas are validated at runtime via **Pydantic v2**.

---

## 1. Story Record Schema (`StoryRecord`)

Every folklore narrative and urban legend is stored as a structured JSON object matching `StoryRecord`.

| Field Name | Type | Required | Description | Constraints / Allowed Values |
|---|---|---|---|---|
| `id` | `str` | Yes | Stable record identifier | Format: `^[A-Z]{2}-(FOLK\|URBAN)-[0-9]{3,}$` (e.g. `IN-FOLK-001`, `JP-URBAN-010`) |
| `title` | `str` | Yes | Canonical title of the narrative | Min length: 2 |
| `country_code` | `str` | Yes | Target ISO 2-letter country code | One of the 15 supported countries (`IN`, `US`, `JP`, etc.) |
| `region_or_community` | `str` | No | Specific cultural, ethnic, regional, or Indigenous provenance | e.g. "Navajo Nation", "Yoruba", "Kyoto Prefecture", "Bavaria" |
| `category` | `CategoryEnum` | Yes | Primary archive partition | `folklore` or `urban_legend` |
| `subtype` | `str` | No | Sub-classification | e.g. `ghost_story`, `trickster_tale`, `cryptid`, `warning_legend`, `kaidan` |
| `summary` | `str` | Yes | Concise narrative synopsis | Min length: 10 chars |
| `long_description` | `str` | No | Detailed narrative text or translation | Optional; omitted in metadata-only records |
| `alternate_names` | `list[str]` | No | Regional, linguistic, or historical variant titles | Default: `[]` |
| `language` | `str` | Yes | Primary language code of this record text | Default: `"en"` |
| `motifs` | `list[str]` | No | Thompson motif index codes or folk motif tags | e.g. `["E235.1", "J1791"]` |
| `themes` | `list[str]` | No | Curatorial tags / themes | e.g. `["shapeshifting", "haunted_crossing", "vengeful_spirit"]` |
| `historical_period` | `str` | No | Earliest documented era or origin | e.g. "Edo Period", "Late 20th Century", "Vedic Era" |
| `variant_notes` | `str` | No | Editorial commentary on regional variations | |
| `sources` | `list[StorySource]` | Yes | Bibliographic or web source citations | At least 1 validated source required |
| `source_type` | `str` | Yes | Primary source classification | e.g. `academic_archive`, `public_domain_anthology`, `encyclopedia` |
| `license` | `str` | Yes | Legal copyright or license declaration | e.g. "Public Domain", "CC BY-SA 4.0", "Rights Managed" |
| `rights_status` | `RightsStatusEnum` | Yes | Rights assessment status | See enum values below; default: `needs_rights_review` |
| `attribution_text` | `str` | No | Mandatory attribution statement | e.g. "Adapted from Joseph Jacobs (1892)" |
| `canonical_url` | `str` | No | Primary canonical URL | Must parse as valid HTTP/HTTPS URL |
| `retrieved_at` | `datetime` | No | ISO timestamp when record was sourced | |
| `verification_status` | `VerificationStatusEnum` | Yes | Editorial verification stage | `verified`, `needs_review`, `rejected` |
| `content_origin` | `ContentOriginEnum` | Yes | Content origin classification | See enum values below |
| `created_at` | `datetime` | Yes | Record creation timestamp | ISO 8601 UTC |
| `updated_at` | `datetime` | Yes | Record modification timestamp | ISO 8601 UTC |
| `record_version` | `str` | Yes | Semantic version of the record | Default: `"1.0.0"` |

---

## 2. Controlled Enums

### A. Primary Category (`CategoryEnum`)
- `folklore`: Traditional narratives, ancient myths, oral traditions, cultural beings, and historical folklore.
- `urban_legend`: Modern legends, circulating rumors, contemporary folklore, and ghost stories.

### B. Verification Status (`VerificationStatusEnum`)
- `verified`: Record has been verified against documented sources and approved for public display.
- `needs_review`: Candidate record awaiting cultural, geographic, or source verification.
- `rejected`: Record rejected due to fabricated sources, factual inaccuracy, or rights violation.

### C. Rights Status (`RightsStatusEnum`)
- `approved`: Clear legal permission to distribute text and metadata (e.g. CC0, CC BY, original summary).
- `metadata_only`: Only bibliographic citations, metadata, and links may be displayed; full text withheld.
- `public_domain_verified`: Text verified as public domain in author jurisdiction and under US law (pre-1929).
- `permission_required`: Source requires written permission before text reproduction.
- `needs_rights_review`: Default status for unreviewed incoming data (e.g. raw CSV).
- `restricted`: Commercial or proprietary source; strict reference only.
- `unknown`: Source license unknown; treated as restricted until audited.

### D. Content Origin (`ContentOriginEnum`)
- `licensed_dataset`: Sourced from an openly licensed dataset (e.g. CC BY 4.0).
- `public_domain_source`: Transcribed from a verified historical public-domain publication.
- `original_summary`: Written by KathaYantra editors based on documented folklore research.
- `metadata_only`: Citation and entity metadata only; no prose body stored.
- `user_contributed`: Submitted by a community contributor with explicit licensing.
- `ai_generated_fiction`: Generated by local AI (Gemma 2). Strictly segregated from authentic folklore.

---

## 3. Story Source Schema (`StorySource`)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `str` | Yes | Institutional archive, publication, or website name |
| `url` | `str` | Yes | Validated HTTP/HTTPS URL |
| `source_type` | `str` | Yes | e.g. `book`, `journal`, `archive_portal`, `oral_collection` |
| `citation` | `str` | No | Formal Chicago/MLA bibliographic citation |
| `access_date` | `str` | No | ISO date when source was referenced |

---

## 4. Annotated Story Record Example

```json
{
  "id": "IN-FOLK-001",
  "title": "The Demon with the Matted Hair",
  "country_code": "IN",
  "region_or_community": "Varanasi / Buddhist Jataka Tradition",
  "category": "folklore",
  "subtype": "jataka_tale",
  "summary": "Prince Brahmadatta encounters the demon Sticky-Hair in a forest. When all his weapons are caught in the demon's enchanted fur, the prince confronts the creature with fearless resolve, compelling the demon to repent.",
  "alternate_names": [
    "Pancasavudha Jataka",
    "Jataka 55"
  ],
  "language": "en",
  "motifs": [
    "G510.4",
    "D1654.4.1"
  ],
  "themes": [
    "courage",
    "monsters",
    "buddhist_moral"
  ],
  "historical_period": "Classical Ancient India (circa 4th century BCE)",
  "sources": [
    {
      "name": "Indian Fairy Tales",
      "url": "https://www.gutenberg.org/ebooks/7128",
      "source_type": "public_domain_book",
      "citation": "Jacobs, Joseph. Indian Fairy Tales. London: David Nutt, 1892, pp. 194-198.",
      "access_date": "2026-10-29"
    }
  ],
  "source_type": "public_domain_anthology",
  "license": "Public Domain in the United States",
  "rights_status": "public_domain_verified",
  "attribution_text": "Collected by Joseph Jacobs (1892); based on traditional Jataka Pali canon.",
  "canonical_url": "https://www.gutenberg.org/ebooks/7128",
  "verification_status": "verified",
  "content_origin": "public_domain_source",
  "created_at": "2026-10-29T12:00:00Z",
  "updated_at": "2026-10-29T12:00:00Z",
  "record_version": "1.0.0"
}
```

---

## 5. Country Seed File Schema (`CountrySeedFile`)

Every country seed file (e.g. `data/seed/folklore/IN.json` or `data/seed/urban_legends/US.json`) follows this structure:

```json
{
  "country_code": "IN",
  "category": "folklore",
  "records": [],
  "metadata": {
    "total_records": 0,
    "target_count": 10,
    "status": "pending_curation",
    "last_updated": "2026-10-29T12:00:00Z"
  }
}
```

