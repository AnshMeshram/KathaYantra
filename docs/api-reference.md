# KathaYantra REST API Reference (v1.0.0)

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

All public endpoints are served under the versioned prefix `/api/v1`.  
Interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running the server locally.

---

## 1. Global Conventions & Standards

### Standard Collection Response Envelope
```json
{
  "data": [ ... ],
  "pagination": {
    "total": 300,
    "limit": 10,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "filter_name": "value"
  }
}
```

### Standard Single-Record Response Envelope
```json
{
  "data": { ... }
}
```

### Standard Error Response Envelope
```json
{
  "error_code": "STORY_NOT_FOUND",
  "message": "Story record 'IN-FOLK-999' was not found in the verified archive.",
  "detail": null
}
```

### Security Headers
Every HTTP response automatically includes standard defensive headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## 2. Endpoint Inventory Matrix

| Method | Path | Summary | Auth | Offline? | Requires Ollama? |
|---|---|---|:---:|:---:|:---:|
| `GET` | `/` | Root API metadata and documentation links | None | Yes | No |
| `GET` | `/api/v1/health` | System health, dataset flags, story totals | None | Yes | No |
| `GET` | `/api/v1/health/ollama` | Dedicated Ollama & Gemma 2 diagnostic probe | None | Yes | Optional |
| `GET` | `/api/v1/countries` | List all 15 supported target countries | None | Yes | No |
| `GET` | `/api/v1/countries/{country_code}` | Get country profile and cultural context | None | Yes | No |
| `GET` | `/api/v1/countries/{country_code}/stats` | Country published story counts & quota gaps | None | Yes | No |
| `GET` | `/api/v1/countries/{country_code}/stories` | Browse stories for a specific country | None | Yes | No |
| `GET` | `/api/v1/folklore` | List and filter traditional folklore narratives | None | Yes | No |
| `GET` | `/api/v1/folklore/{story_id}` | Get folklore story detail | None | Yes | No |
| `GET` | `/api/v1/urban-legends` | List and filter documented modern urban legends | None | Yes | No |
| `GET` | `/api/v1/urban-legends/{story_id}` | Get urban legend story detail | None | Yes | No |
| `GET` | `/api/v1/stories/{story_id}` | Unified story detail (folklore or urban legend) | None | Yes | No |
| `GET` | `/api/v1/stories/{story_id}/sources` | Documented bibliographic sources for a story | None | Yes | No |
| `GET` | `/api/v1/stories/{story_id}/related` | Discover related narratives by motif/theme | None | Yes | No |
| `GET` | `/api/v1/search` | Full catalogue search with filters | None | Yes | No |
| `GET` | `/api/v1/search/suggest` | Bounded autocomplete suggestions | None | Yes | No |
| `GET` | `/api/v1/sources` | Directory of 17 external archives & APIs | None | Yes | No |
| `GET` | `/api/v1/sources/{source_id}` | Detail for external source registry entry | None | Yes | No |
| `GET` | `/api/v1/dataset/manifest` | Real-time computed dataset manifest | None | Yes | No |
| `GET` | `/api/v1/dataset/coverage` | 15-country quota coverage breakdown | None | Yes | No |
| `GET` | `/api/v1/dataset/quality` | Seed file integrity and candidate metrics | None | Yes | No |
| `GET` | `/api/v1/dataset/quality/source-readiness` | AI retrieval readiness audit (100% verified) | None | Yes | No |
| `GET` | `/api/v1/ai/health` | AI service status and retrieval index metrics | None | Yes | Optional |
| `POST` | `/api/v1/ai/ask` | Grounded question answering (RAG) | None | Yes | Yes (Fallback available) |
| `POST` | `/api/v1/ai/compare` | Cross-cultural story comparison | None | Yes | Yes (Fallback available) |
| `POST` | `/api/v1/ai/generate-story` | Quarantined creative fiction generation | None | Yes | Yes |

---

## 3. Endpoints in Detail

### 3.1 Countries Endpoints

#### `GET /api/v1/countries`
Returns the canonical list of all 15 supported countries.
- **Query Parameters:** `limit` (int, 1–100, default 20), `offset` (int, default 0).
- **Response Model:** `PaginatedResponse[CountryRecord]`

#### `GET /api/v1/countries/{country_code}`
Returns metadata, cultural context, and target quotas for a country.
- **Path Parameters:** `country_code` (e.g., `IN`, `US`, `JP`, case-insensitive).
- **Error Behavior:** Returns `404 Not Found` if `country_code` is not in the 15 supported countries.

#### `GET /api/v1/countries/{country_code}/stats`
Returns live calculated statistics for a country derived directly from eligible stories:
- `folklore_count` (10)
- `urban_legend_count` (10)
- `total_count` (20)
- `folklore_target` (10)
- `urban_legend_target` (10)
- `folklore_gap` (0)
- `urban_legend_gap` (0)
- `is_quotas_met` (`true`)
- `source_count` (number of unique citations)

#### `GET /api/v1/countries/{country_code}/stories`
Browse stories associated with a country.
- **Query Parameters:**
  - `category`: `folklore` or `urban_legend`
  - `language`: ISO language code
  - `motif`: Motif keyword or Thompson ID
  - `q`: Substring search query
  - `sort_by`: `id`, `title`, `created_at` (default: `id`)
  - `sort_order`: `asc` or `desc` (default: `asc`)
  - `limit`: 1–100 (default: 10)
  - `offset`: ge 0 (default: 0)

---

### 3.2 Folklore Endpoints

#### `GET /api/v1/folklore`
List published traditional folklore narratives.
- **Query Parameters:** `country_code`, `region`, `language`, `motif`, `theme`, `q`, `sort_by`, `sort_order`, `limit`, `offset`.
- **Response Model:** `PaginatedResponse[StoryRecord]`
- **Archival Rule:** Never returns urban legends or AI-generated fiction.

#### `GET /api/v1/folklore/{story_id}`
Retrieve a single folklore story.
- **Path Parameters:** `story_id` (e.g. `IN-FOLK-001`, `BR-FOLK-003`).
- **Error Behavior:** Returns `404 Not Found` if the record does not exist or if it belongs to the `urban_legend` category.

---

### 3.3 Urban Legend Endpoints

#### `GET /api/v1/urban-legends`
List published contemporary urban legends, haunted sites, and modern rumors.
- **Query Parameters:** `country_code`, `region`, `language`, `motif`, `theme`, `q`, `sort_by`, `sort_order`, `limit`, `offset`.
- **Response Model:** `PaginatedResponse[StoryRecord]`
- **Archival Rule:** Never returns traditional folklore or AI-generated fiction.

#### `GET /api/v1/urban-legends/{story_id}`
Retrieve a single urban legend record.
- **Path Parameters:** `story_id` (e.g. `JP-URBAN-001`, `US-URBAN-002`).
- **Error Behavior:** Returns `404 Not Found` if the record does not exist or if it belongs to the `folklore` category.

---

### 3.4 Unified Story & Provenance Endpoints

#### `GET /api/v1/stories/{story_id}`
Resolves any authentic published record across either category.
- **Path Parameters:** `story_id` (e.g. `IE-FOLK-001` or `MX-URBAN-001`).
- **Response Model:** `SingleResponse[StoryRecord]`

#### `GET /api/v1/stories/{story_id}/sources`
Returns the authentic, stored bibliographic references supporting the story.
- **Response Model:** `SingleResponse[list[StorySource]]`
- **Integrity Rule:** Citations are extracted from stored metadata (`url`, `publisher`, `rights_status`, `attribution_text`). No model-invented URLs.

#### `GET /api/v1/stories/{story_id}/related`
Discovers related narratives based on curated cross-references, shared Thompson motifs, or thematic archetypes.
- **Query Parameters:** `limit` (1–20, default 5).
- **Response Model:** `SingleResponse[list[RelatedStoryItem]]`
- **Output Fields:** `story_id`, `title`, `category`, `country_code`, `summary`, `relationship_basis`, `shared_motifs`, `shared_themes`.
- **Integrity Rule:** Explains the relationship basis; does not claim historical borrowing without documented provenance.

---

### 3.5 Search & Autocomplete Endpoints

#### `GET /api/v1/search`
High-precision catalogue search over titles, alternate names, summaries, motifs, and communities.
- **Query Parameters:**
  - `q`: Search string (min 1, max 200 chars).
  - `category`: Optional filter (`folklore` or `urban_legend`).
  - `country_code`: Optional 2-letter ISO country code.
  - `language`: Optional language filter.
  - `motif`: Optional motif tag.
  - `limit`: 1–50 (default: 10).
  - `offset`: ge 0 (default: 0).
- **Behavior:** Powered by SQLite FTS5 BM25 with in-memory deterministic fallback. Returns empty list if no matches found. Does not depend on Ollama.

#### `GET /api/v1/search/suggest`
Bounded autocomplete suggestions.
- **Query Parameters:** `q` (min 2, max 100 chars), `limit` (1–20, default 10).
- **Response Model:** `SingleResponse[list[SearchSuggestion]]`
- **Output Fields:** `text`, `suggestion_type` (`title`, `alternate_name`, `motif`, `region`), `category`, `country_code`.

---

### 3.6 Sources Registry Endpoints

#### `GET /api/v1/sources`
Directory of the 17 registered external archives, national libraries, and open-data APIs.
- **Query Parameters:** `limit` (default 20), `offset` (default 0).
- **Security Rule:** Sensitive fields (`api_key`, `secret`, `credentials`) are stripped before returning.

#### `GET /api/v1/sources/{source_id}`
Detailed registry entry for an external repository (e.g. `wikimedia_wikipedia_api`, `library_of_congress_api`, `cnfcp_iphan_brazil`).
- **Path Parameters:** `source_id`.
- **Error Behavior:** Returns `404 Not Found` if source ID is not registered.

---

### 3.7 Dataset Governance Endpoints

#### `GET /api/v1/dataset/manifest`
Computed manifest reconciling published stories against target quotas.
- **Response Model:** `SingleResponse[DatasetManifest]`
- **Key Fields:** `current_actual_counts.total_records` (300), `required_record_count` (300), `folklore_counts_by_country`, `urban_legend_counts_by_country`.

#### `GET /api/v1/dataset/coverage`
Detailed country-by-country and category-by-category quota coverage report.
- **Response Model:** `SingleResponse[ArchiveCoverageReport]`
- **Key Fields:** `actual_total_records` (300), `completion_percentage` (100.0), `countries_fully_met` (15), `partitions_met` (30), `total_partitions` (30).

#### `GET /api/v1/dataset/quality`
Seed file validation, candidate staging, and index compile status.
- **Response Model:** `SingleResponse[DatasetQualityResponse]`
- **Key Fields:** `status` ("healthy"), `published_records` (300), `seed_files_valid` (30/30), `retrieval_index_count` (300).

#### `GET /api/v1/dataset/quality/source-readiness`
Real-time audit report confirming all 300 records satisfy AI retrieval readiness standards.
- **Response Model:** `SingleResponse[SourceReadinessResponse]`
- **Key Fields:** `total_records_audited` (300), `accepted_for_ai` (300), `flagged_records_count` (0), `acceptance_rate_percent` (100.0), `status` ("pass").

---

### 3.8 Local AI Archivist Endpoints

#### `GET /api/v1/health/ollama`
Dedicated diagnostic probe for Ollama daemon connectivity and configured Gemma 2 model readiness.
- **Response Fields:** `ollama_available`, `base_url`, `model_configured`, `model_available`, `available_models`, `response_time_ms`, `error_message`.

#### `POST /api/v1/ai/ask`
Ask the Archivist: grounded question answering using SQLite FTS5 retrieval and local Gemma 2 inference.
- **Request Body (`AIQuestionRequest`):**
  ```json
  {
    "query": "Who is Saci-Perere in Brazilian folklore?",
    "country_code": "BR",
    "max_context_records": 5
  }
  ```
- **Response Model (`AIQuestionResponse`):** Grounded answer, `answer_type` (`grounded_answer`, `insufficient_evidence`, `offline_fallback`), authentic citations from `StorySource` metadata, `model_used`, `disclaimer`.

#### `POST /api/v1/ai/compare`
Cross-Cultural Story Comparison: compares 2 to 5 verified records.
- **Request Body (`AIComparisonRequest`):**
  ```json
  {
    "story_ids": ["IE-FOLK-006", "MX-URBAN-001"],
    "aspect_notes": "Compare vocal manifestation and water associations"
  }
  ```
- **Response Model (`AIComparisonResponse`):** Structured comparative sections (`similarities`, `differences`, `cultural_context`, `uncertain_details`), citations, `narrative_synthesis`.

#### `POST /api/v1/ai/generate-story`
Creative Fiction Generation: generates modern synthetic fiction inspired by authentic folklore motifs.
- **Request Body (`AIFictionRequest`):**
  ```json
  {
    "inspiration_story_ids": ["US-URBAN-001"],
    "setting": "Point Pleasant wetlands",
    "atmosphere": "quiet dread",
    "save_record": true
  }
  ```
- **Response Model (`AIFictionResponse`):** Returns HTTP 201 Created. Instantiates `GeneratedFictionRecord` (`id: AI-FIC-xxx`) with mandatory non-authentic disclaimer. Quarantined in `data/processed/generated_fiction/`.
