# KathaYantra — Backend Integration Audit for Frontend

> **Audited:** Phase 0 Frontend Integration  
> **Backend Version:** 0.1.0  
> **Base URL:** `http://127.0.0.1:8000`  
> **API Prefix:** `/api/v1`  
> **CORS Allowed Origins:** `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:5173`, `http://127.0.0.1:5173`

---

## 1. Complete API Route Directory

### 1.1 System Endpoints

| Method | Path | Response | Description |
|--------|------|----------|-------------|
| GET | `/` | JSON object | Root status with project name, version, tagline, links |
| GET | `/api/v1/health` | JSON object | System health: dataset flags, story totals, Ollama status |
| GET | `/api/v1/health/ollama` | JSON object | Ollama AI model readiness diagnostic |

### 1.2 Country Endpoints

| Method | Path | Response | Query Params | Description |
|--------|------|----------|-------------|-------------|
| GET | `/api/v1/countries` | `PaginatedResponse<CountryRecord>` | `limit` (1–100, default 20), `offset` (≥0) | List all 15 supported countries |
| GET | `/api/v1/countries/{country_code}` | `SingleResponse<CountryRecord>` | — | Get single country by ISO alpha-2 code |
| GET | `/api/v1/countries/{country_code}/stats` | `SingleResponse<CountryStatsResponse>` | — | Published counts, targets, quotas, gaps |
| GET | `/api/v1/countries/{country_code}/stories` | `PaginatedResponse<StoryRecord>` | `category`, `language`, `motif`, `q`, `sort_by`, `sort_order`, `limit`, `offset` | Stories filtered by country |

### 1.3 Folklore Endpoints

| Method | Path | Response | Query Params | Description |
|--------|------|----------|-------------|-------------|
| GET | `/api/v1/folklore` | `PaginatedResponse<StoryRecord>` | `country_code`, `region`, `language`, `motif`, `theme`, `q`, `sort_by`, `sort_order`, `limit`, `offset` | List/filter folklore records |
| GET | `/api/v1/folklore/{story_id}` | `SingleResponse<StoryRecord>` | — | Get folklore story detail |

### 1.4 Urban Legend Endpoints

| Method | Path | Response | Query Params | Description |
|--------|------|----------|-------------|-------------|
| GET | `/api/v1/urban-legends` | `PaginatedResponse<StoryRecord>` | `country_code`, `region`, `language`, `motif`, `theme`, `q`, `sort_by`, `sort_order`, `limit`, `offset` | List/filter urban legends |
| GET | `/api/v1/urban-legends/{story_id}` | `SingleResponse<StoryRecord>` | — | Get urban legend detail |

### 1.5 Unified Story Endpoints

| Method | Path | Response | Query Params | Description |
|--------|------|----------|-------------|-------------|
| GET | `/api/v1/stories/{story_id}` | `SingleResponse<StoryRecord>` | — | Resolve any story by ID |
| GET | `/api/v1/stories/{story_id}/sources` | `SingleResponse<StorySource[]>` | — | Bibliographic citations |
| GET | `/api/v1/stories/{story_id}/related` | `SingleResponse<RelatedStoryItem[]>` | `limit` (1–20, default 5) | Related stories by motif/theme |

### 1.6 Search Endpoints

| Method | Path | Response | Query Params | Description |
|--------|------|----------|-------------|-------------|
| GET | `/api/v1/search` | `PaginatedResponse<StoryRecord>` | `q` (required), `category`, `country_code`, `language`, `motif`, `limit` (1–50), `offset` | Full-text search with FTS5 + fallback |
| GET | `/api/v1/search/suggest` | `SingleResponse<SearchSuggestion[]>` | `q` (min 2 chars), `limit` (1–20) | Autocomplete suggestions |

### 1.7 Source Registry Endpoints

| Method | Path | Response | Description |
|--------|------|----------|-------------|
| GET | `/api/v1/sources` | `PaginatedResponse<SourceRegistryItem>` | List 17 external source registries |
| GET | `/api/v1/sources/{source_id}` | `SingleResponse<SourceRegistryItem>` | Get source registry detail |

### 1.8 Dataset Governance Endpoints

| Method | Path | Response | Description |
|--------|------|----------|-------------|
| GET | `/api/v1/dataset/manifest` | `SingleResponse<DatasetManifest>` | Real-time computed dataset manifest |
| GET | `/api/v1/dataset/coverage` | `SingleResponse<ArchiveCoverageReport>` | 15-country coverage report |
| GET | `/api/v1/dataset/quality` | `SingleResponse<DatasetQualityResponse>` | Data quality and seed file integrity |
| GET | `/api/v1/dataset/quality/source-readiness` | `SingleResponse<SourceReadinessResponse>` | AI readiness audit |

### 1.9 AI Archivist Endpoints

| Method | Path | Response | Description |
|--------|------|----------|-------------|
| GET | `/api/v1/ai/health` | `AIOllamaHealthResponse` | AI subsystem status |
| POST | `/api/v1/ai/ask` | `AIQuestionResponse` | Grounded Q&A (RAG) |
| POST | `/api/v1/ai/compare` | `AIComparisonResponse` | Story comparison |
| POST | `/api/v1/ai/generate-story` | `AIFictionResponse` | Fiction generation (201 Created) |

**Total: 26 endpoints** (1 root + 25 under `/api/v1`)

---

## 2. Response Envelope Contracts

### 2.1 Paginated Collection

```typescript
interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;     // Total matching items
    limit: number;     // Page size (1–100)
    offset: number;    // Starting index
    has_next: boolean;
    has_prev: boolean;
  };
  meta: Record<string, any>; // Query context
}
```

### 2.2 Single Record

```typescript
interface SingleResponse<T> {
  data: T;
}
```

### 2.3 Error Response

```typescript
interface ErrorResponse {
  error_code: string;   // Machine-readable (e.g. "STORY_NOT_FOUND")
  message: string;      // Human-readable
  detail: any | null;   // Optional diagnostics
}
```

---

## 3. Core Data Schemas

### 3.1 StoryRecord (Primary Entity)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | Yes | Format: `{CC}-(FOLK\|URBAN)-{NNN}` (e.g. `IN-FOLK-001`) |
| `schema_version` | string | — | Default `"2.0.0"` |
| `record_version` | string | — | Default `"1.0.0"` |
| `title` | string | Yes | 2–300 chars |
| `slug` | string | — | Auto-generated URL-safe slug |
| `country_code` | string | Yes | ISO 3166-1 alpha-2 (one of 15 supported) |
| `category` | enum | Yes | `"folklore"` or `"urban_legend"` |
| `subtype` | string? | No | Sub-genre (e.g. `ghost_story`, `jataka_tale`, `kaidan`) |
| `summary` | string | Yes | 10–5000 chars |
| `long_description` | string? | No | Extended text up to 250,000 chars |
| `alternate_names` | string[] | — | Variant titles, indigenous names |
| `language` | string | — | Default `"en"` (ISO 639-1) |
| `alternate_languages` | string[] | — | Other telling languages |
| `motifs` | string[] | — | Thompson motif index codes |
| `themes` | string[] | — | Thematic tags (e.g. `"wisdom"`, `"ghost"`) |
| `historical_period` | string? | No | Era or earliest documented period |
| `region_or_community` | string? | No | Cultural/ethnic/regional community (text) |
| `community_attributions` | string[] | — | Sovereign tribal/ethnic groups |
| `geographic_associations` | string[] | — | Place names (NO lat/lng coordinates) |
| `variant_notes` | string? | No | Regional variant documentation |
| `related_record_ids` | string[] | — | Cross-reference IDs |
| `sources` | StorySource[] | Yes | Min 1 documented source required |
| `source_type` | string | — | Default `"reference"` |
| `license` | string | — | Copyright/license notice |
| `rights_status` | enum | — | `approved`, `metadata_only`, `public_domain_verified`, etc. |
| `attribution_text` | string? | No | Mandatory attribution string |
| `canonical_url` | string? | No | Authoritative link |
| `retrieved_at` | datetime? | No | Data retrieval timestamp |
| `verification_status` | enum | — | `verified`, `needs_review`, `rejected` |
| `content_origin` | enum | — | `licensed_dataset`, `public_domain_source`, etc. |
| `created_at` | datetime | — | ISO 8601 UTC |
| `updated_at` | datetime | — | ISO 8601 UTC |

### 3.2 StorySource (Bibliographic Citation)

| Field | Type | Required |
|-------|------|----------|
| `id` | string? | No |
| `title` | string | — |
| `publisher` | string | — |
| `name` | string | — |
| `url` | string | Yes |
| `canonical_url` | string? | No |
| `external_id` | string? | No |
| `source_type` | string | — |
| `language` | string | — |
| `published_at` | string? | No |
| `license_name` | string? | No |
| `rights_status` | enum | — |
| `attribution_text` | string? | No |
| `full_text_reuse_allowed` | boolean | — |
| `citation` | string? | No |

### 3.3 CountryRecord

| Field | Type | Notes |
|-------|------|-------|
| `code` | string | ISO alpha-2 |
| `name` | string | Standard English name |
| `display_name` | string | Localized title |
| `region` | string | Geographic cultural region |
| `primary_languages` | string[] | ISO 639-1 codes |
| `regions_or_communities` | string[] | Key regional designations |
| `cultural_context` | string | Folkoric tradition overview |
| `record_targets` | object | `{ folklore: number, urban_legends: number }` |
| `enabled` | boolean | — |

### 3.4 CountryStatsResponse

| Field | Type |
|-------|------|
| `country_code` | string |
| `country_name` | string |
| `folklore_count` | number |
| `urban_legend_count` | number |
| `total_count` | number |
| `folklore_target` | number |
| `urban_legend_target` | number |
| `total_target` | number |
| `folklore_gap` | number |
| `urban_legend_gap` | number |
| `total_gap` | number |
| `is_quotas_met` | boolean |
| `source_count` | number |
| `cultural_context` | string |

### 3.5 RelatedStoryItem

| Field | Type |
|-------|------|
| `story_id` | string |
| `title` | string |
| `category` | string |
| `country_code` | string |
| `summary` | string |
| `relationship_basis` | string |
| `shared_motifs` | string[] |
| `shared_themes` | string[] |

### 3.6 SearchSuggestion

| Field | Type |
|-------|------|
| `text` | string |
| `suggestion_type` | string (`title`, `motif`, `alternate_name`, `region`) |
| `category` | string? |
| `country_code` | string? |

### 3.7 AI Request/Response Schemas

**AIQuestionRequest:** `{ question, country_code?, category?, max_records? }`  
**AIQuestionResponse:** `{ question, answer, answer_type, supporting_story_ids[], sources[], retrieval_status, limitations?, model_provider, model_tag, prompt_version, generated_at }`  
**AIComparisonRequest:** `{ story_ids[] (2–5), aspect_notes? }`  
**AIComparisonResponse:** `{ summary, compared_story_ids[], similarities[], differences[], cultural_context[], uncertain_details[], sources[], model_tag }`  
**AIFictionRequest:** `{ inspiration_story_ids[] (1–5), setting?, atmosphere?, narrative_style?, creative_prompt? }`  
**AIFictionResponse:** `{ fiction_record, saved_path?, model_tag }`  

---

## 4. Data Architecture

### 4.1 Dataset Structure

```
data/
├── seed/
│   ├── countries.json           # 15 CountryRecord entries
│   ├── source_registry.json     # 17 SourceRegistryItem entries
│   ├── folklore/
│   │   ├── BR.json ... US.json  # 15 files, 10 records each
│   └── urban_legends/
│       ├── BR.json ... US.json  # 15 files, 10 records each
├── manifests/
├── processed/
│   ├── candidates/
│   ├── generated_fiction/
│   └── retrieval/               # SQLite FTS5 index
└── schemas/
```

### 4.2 Supported Countries (15)

| Code | Country | Region |
|------|---------|--------|
| IN | India | South Asia |
| US | United States | North America |
| JP | Japan | East Asia |
| MX | Mexico | Latin America |
| IE | Ireland | Western Europe |
| GB | United Kingdom | Western Europe |
| BR | Brazil | South America |
| GR | Greece | Southern Europe |
| CN | China | East Asia |
| NG | Nigeria | West Africa |
| KR | South Korea | East Asia |
| PH | Philippines | Southeast Asia |
| ID | Indonesia | Southeast Asia |
| EG | Egypt | North Africa |
| DE | Germany | Central Europe |

### 4.3 Record Counts (Verified)

- **300 total records** (150 folklore + 150 urban legends)
- **20 per country** (10 folklore + 10 urban legends)
- All records have `verification_status: "verified"`
- All records pass `PublicationPolicy.evaluate_eligibility()`
- All 300 have at least one `StorySource` with valid HTTP URL
- All 300 have `geographic_associations` (text place names — NO lat/lng)
- All 300 have `region_or_community` (text)

---

## 5. Frontend Integration Notes

### 5.1 Critical Limitations

1. **No geographic coordinates exist.** Stories have text `geographic_associations` (e.g., "Ujjain", "Amazon River") but no latitude/longitude. The map must geocode from country code, not from story coordinates.

2. **No image URLs in data.** Story records do not contain image references. All imagery must be sourced externally and mapped via the image manifest.

3. **Ollama is optional.** AI endpoints require a running Ollama instance with `gemma2:latest`. Frontend must gracefully handle AI unavailability.

4. **In-memory repository.** All data loads into memory at startup. No database. No mutations through the API. Read-only after boot.

5. **CORS is pre-configured** for ports 3000 and 5173.

### 5.2 Query Parameter Reference

**Sorting:** `sort_by` accepts `id`, `title`, `country_code`, `created_at`. `sort_order` accepts `asc`, `desc`.

**Pagination:** `limit` (1–100), `offset` (≥0). Search limit max is 50.

**Filtering:** `category` (`folklore` | `urban_legend`), `country_code` (2-letter), `region` (substring match), `language` (ISO 639-1), `motif` (Thompson code substring), `theme` (keyword substring).

**Search:** `q` parameter for full-text across title, alternate names, summary, motifs, themes, region.

### 5.3 Error Handling

All errors return `{ error_code, message, detail }`. HTTP status codes:
- 404: `STORY_NOT_FOUND`, `COUNTRY_NOT_FOUND`
- 422: `VALIDATION_ERROR` (with Pydantic error detail array)
- 500: `INTERNAL_SERVER_ERROR`

### 5.4 Map Behavior: Supported vs Unsupported Countries

The frontend map must distinguish:
- **15 supported countries** → Show story counts, allow click-through to country detail
- **All other countries** → Show tooltip: *"Stories coming soon. Our archive is still growing. Folklore and urban legends from this country will be available soon."*

---

## 6. Security Headers

The backend adds these headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## 7. Startup Sequence

1. Backend loads `.env` configuration
2. `story_repository.load()` pre-caches all 300 records, 15 countries, 17 sources
3. Stories filtered through `PublicationPolicy` and `VerificationStatus` checks
4. FTS5 SQLite index available for search if `retrieval_index.db` exists
5. Ollama health checked non-blocking (won't fail startup if offline)

