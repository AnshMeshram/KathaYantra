# KathaYantra External API and Data Source Integration Status

> **Compliance Principle:**  
> *Separate implemented and tested connectors, credential-dependent APIs, and reference-only discovery archives truthfully. Never claim an endpoint is functional without reproducible tests.*

---

## 1. Integration Status Matrix

| Source ID | Source Name | Source Type | Status Classification | Auth Required | Implemented Module | Mocked Tests | Live Verification |
|---|---|---|---|:---:|---|:---:|:---:|
| `wikimedia_wikipedia_api` | Wikimedia / Wikipedia REST API | Encyclopedic API | **Implemented & Tested** | No | `app/integrations/mediawiki.py` | 4/4 PASS | **VERIFIED** |
| `wikidata_sparql` | Wikidata SPARQL Endpoint | Knowledge Graph API | **Implemented & Tested** | No | `app/integrations/wikidata.py` | 3/3 PASS | Tested |
| `library_of_congress_api` | Library of Congress JSON API | National Library API | **Implemented & Tested** | No | `app/integrations/library_of_congress.py` | 3/3 PASS | Handled (Cloudflare 403 gracefully caught) |
| `internet_archive` | Internet Archive Advanced Search | Digital Library API | **Implemented & Tested** | No | `app/integrations/internet_archive.py` | 3/3 PASS | **VERIFIED** |
| `myths_of_ireland` | Myths of Ireland Open Dataset | Structured Open Dataset | **Implemented & Tested** | No | `app/integrations/myths_of_ireland.py` | 2/2 PASS | Cached / Tested |
| `europeana_api` | Europeana REST API | Cultural Heritage API | **Requires Credentials** | Yes (`EUROPEANA_API_KEY`) | `app/integrations/europeana.py` | 4/4 PASS | Dormant fallback tested |
| `japan_search` | Japan Search Platform | Cultural Heritage API | **Implemented & Tested** | Optional | `app/integrations/japan_search.py` | 3/3 PASS | Tested |
| `fairytalez_raw_corpus` | Quarantined Folk Tales CSV | Raw Candidate Corpus | **Implemented & Tested** | No | `app/integrations/csv_importer.py` | 3/3 PASS | **VERIFIED** (2,938 rows) |
| `urban_legends_online` | Urban Legends Online | Discovery Reference | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified no bulk scraping |
| `folklore_ai_github` | Folklore-ai GitHub Repo | Code Reference | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `ncaa_india` | National Cultural Audiovisual Archives | National Archive | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `nichibunken_yokai_db` | Nichibunken Yōkai Database | Academic Database | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `cnfcp_iphan_brazil` | CNFCP / IPHAN Brazil Archive | National Archive | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `duchas_ireland` | Dúchas National Folklore Collection | National Archive | **Requires Permission** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `project_gutenberg` | Project Gutenberg Ebook Archive | Public Domain Ebooks | **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `business_insider_urban_legends`| Business Insider World Urban Legends| Journalistic Overview| **Reference-Only** | No | `app/integrations/reference_only.py` | 1/1 PASS | Verified |
| `wikipedia_urban_legends_category`| Wikipedia Urban Legends Category| Encyclopedic API | **Implemented & Tested** | No | `app/integrations/mediawiki.py` | 4/4 PASS | Tested |

---

## 2. Connector Details & Access Policies

### A. Wikimedia / Wikipedia REST API (`wikimedia_wikipedia_api`)
- **Endpoints:**
  - Search: `https://en.wikipedia.org/w/rest.php/v1/search/page?q={query}&limit={limit}`
  - Summary: `https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
- **Authentication:** None required.
- **User-Agent:** Polite User-Agent header mandated (`KathaYantra/0.3.0`).
- **Data Retrieved:** Page ID, canonical URL, page title, excerpt, description.
- **Full Text Policy:** Full wikitext or HTML bodies are **NOT** copied. Summaries are extracted and stripped of HTML tags.
- **Licensing & Attribution:** CC BY-SA 4.0; attribution and share-alike notices are automatically added to candidate review notes.

### B. Wikidata SPARQL (`wikidata_sparql`)
- **Endpoint:** `https://query.wikidata.org/sparql`
- **Authentication:** None required.
- **Rate Limits & Safeguards:** Constrained SPARQL queries (`LIMIT 50`, `TIMEOUT 25s`), in-memory result caching (TTL: 3600s).
- **Data Retrieved:** Entity QID, label, description, Wikipedia link, language aliases.
- **Licensing & Attribution:** CC0 1.0 (Public Domain Dedication).

### C. Library of Congress JSON API (`library_of_congress_api`)
- **Endpoints:** `https://www.loc.gov/search/?q={query}&fo=json&c={limit}`
- **Authentication:** Public without key; rate-limited. Cloudflare WAF challenges return HTTP 403 which the client handles gracefully.
- **Data Retrieved:** Title, contributors, date, description, item URL, media type, rights statement.
- **Rights Policy:** Pre-1929 items marked `public_domain_verified`; others marked `metadata_only`.

### D. Internet Archive Advanced Search (`internet_archive`)
- **Endpoints:**
  - Search: `https://archive.org/advancedsearch.php`
  - Metadata: `https://archive.org/metadata/{identifier}`
- **Authentication:** None required.
- **Data Retrieved:** Identifier, title, creator, publication date, description, license URL.
- **Full Text Policy:** OCR text and book scans are **NOT** harvested in bulk. Bibliographic citation and summaries only.

### E. Myths of Ireland Open Dataset (`myths_of_ireland`)
- **Format:** Structured JSON index published under CC BY 4.0.
- **Separation of Beings & Places:** Entries describing supernatural beings (e.g. Banshee) or legendary places (e.g. Tara) are flagged in review notes and prevented from automatically publishing as narrative story records.
- **Attribution:** *"Source: Myths of Ireland (CC BY 4.0)"*.

### F. Europeana REST API (`europeana_api`)
- **Endpoint:** `https://api.europeana.eu/record/v2/search.json`
- **Authentication:** Requires `EUROPEANA_API_KEY`.
- **Dormant Graceful Fallback:** If `EUROPEANA_API_KEY` is empty, `check_health()` returns `status="requires_credentials"` and search returns `[]` without raising errors.

### G. Japan Search Platform (`japan_search`)
- **Endpoint:** `https://jpsearch.go.jp/api/item/search`
- **Data Retrieved:** Item ID, Japanese title/name, link, description, database provider.
- **Language Handling:** Preserves Japanese text (`ja`) and romanization.

### H. Quarantined Raw CSV (`fairytalez_raw_corpus`)
- **Source:** `data/raw/folk_tales_deduplicated.csv` (2,938 rows, gitignored).
- **Mapping Review:** Uses `data/manifests/nation_mapping_review.json` to assign ISO codes.
- **Rights Protection:** All candidates set to `needs_rights_review`; full text is quarantined in raw storage and omitted from candidate outputs.

### I. Reference-Only Archives
- **Urban Legends Online:** No public API exists. Scraping is prohibited. Connector returns `reference_only` status.
- **NCAA India, Nichibunken, CNFCP Brazil, Dúchas Ireland:** Official research references lacking bulk APIs. Handled via `ReferenceOnlyConnector` for manual curation.
