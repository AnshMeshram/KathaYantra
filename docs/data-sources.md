# KathaYantra External Data Sources and API Registry

This document records the central data source registry for KathaYantra, documenting potential external repositories, public datasets, cultural archives, and APIs for world folklore and urban legends.

Every entry corresponds to a machine-readable record in [`data/seed/source_registry.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/seed/source_registry.json).

---

## 1. Source Classification Matrix

Sources are categorized using standard status codes:

- `documented_api`: Official, supported REST/SPARQL API available for structured queries.
- `public_dataset`: Downloadable, structured open dataset with documented reuse license.
- `searchable_catalogue`: Searchable web or institutional catalog; no direct programmatic API.
- `reference_only`: Discovery or conceptual reference; scraping or text redistribution prohibited.
- `requires_credentials`: API requires free or licensed registration and developer API key.
- `requires_permission`: Full-text content requires explicit permissions; metadata only.
- `not_yet_verified`: Legacy or unverified endpoint requiring empirical testing before integration.

| ID | Name | Type | Status | Auth Required | Full-Text Clearance | Target Countries |
|---|---|---|---|---|---|---|
| `wikimedia_wikipedia_api` | Wikimedia / Wikipedia REST API | Encyclopedic API | `documented_api` | No | Approved (CC BY-SA) | Global / All 15 |
| `wikidata_sparql` | Wikidata SPARQL Endpoint | Knowledge Graph API | `documented_api` | No | Verified (CC0) | Global / All 15 |
| `library_of_congress_api` | Library of Congress JSON/YAML API | National Library API | `documented_api` | No | Metadata Only | US, Global |
| `internet_archive` | Internet Archive API & Metadata | Digital Library API | `documented_api` | No | Needs Rights Review | Global |
| `myths_of_ireland` | Myths of Ireland Dataset | Open Dataset | `public_dataset` | No | Approved Index (CC BY 4.0) | IE |
| `japan_search` | Japan Search Cultural Heritage API | Cultural Heritage API | `documented_api` | Optional | Metadata Only | JP |
| `europeana_api` | Europeana Digital Heritage REST API | Cultural Heritage API | `requires_credentials` | Yes (API Key) | Metadata CC0 / Media Varies | GR, DE, IE, GB |
| `project_gutenberg` | Project Gutenberg Ebook Archive | Ebook Archive | `public_dataset` | No | Verified Public Domain (pre-1929) | Global |
| `wikipedia_urban_legends_category` | Wikipedia Urban Legends by Country | Encyclopedic API | `documented_api` | No | Approved (CC BY-SA) | Global / All 15 |
| `nichibunken_yokai_db` | Nichibunken Yōkai Database | Academic Database | `searchable_catalogue` | No | Metadata Only / Citation | JP |
| `ncaa_india` | National Cultural Audiovisual Archives | National Archive | `searchable_catalogue` | No | Metadata Only | IN |
| `cnfcp_iphan_brazil` | CNFCP / IPHAN Brazil Folklore Archive | National Archive | `searchable_catalogue` | No | Metadata Only | BR |
| `duchas_ireland` | Dúchas National Folklore Collection | National Archive | `not_yet_verified` | No | Permission Required (NC) | IE |
| `urban_legends_online` | Urban Legends Online | Discovery Reference | `reference_only` | No | Prohibited (Proprietary Retellings) | Global, US |
| `urban_legends_archive` | Urban Legends Archive | Discovery Reference | `reference_only` | No | Prohibited (Proprietary Retellings) | Global, US, GB |
| `folklore_ai_github` | Folklore-ai GitHub Repository | Code Reference | `reference_only` | No | Synthetic Content (Not Authentic) | IN |
| `business_insider_urban_legends` | Business Insider World Urban Legends | Journalistic Overview | `reference_only` | No | Restricted / Citation Only | Global |

---

## 2. Detailed Source Profiles

### 1. Wikimedia / Wikipedia REST API
- **ID:** `wikimedia_wikipedia_api`
- **Canonical URL:** https://en.wikipedia.org/
- **Documentation:** https://www.mediawiki.org/wiki/API:REST_API
- **API Status:** `documented_api`
- **Rate Limit Policy:** Max 200 requests/sec with custom `User-Agent: KathaYantraBot/0.1 (folklore-archive)` header.
- **Content Format:** JSON.
- **Role in KathaYantra:** Automated retrieval of encyclopedic folklore summaries, historical variants, alternate entity spellings, and bibliographic citations.
- **Licensing:** Creative Commons Attribution-ShareAlike (CC BY-SA 4.0 / 3.0). Attribution is required on all displayed summaries.

### 2. Wikidata SPARQL Query Service
- **ID:** `wikidata_sparql`
- **Canonical URL:** https://www.wikidata.org/
- **Documentation:** https://query.wikidata.org/sparql
- **API Status:** `documented_api`
- **Rate Limit Policy:** 60-second query timeout limit; max 5 concurrent requests per client IP.
- **Content Format:** SPARQL JSON.
- **Role in KathaYantra:** Structured ontology linking, geographic coordinates for folklore locations (e.g., haunted sites, mythic landmarks), and multilingual labels.
- **Licensing:** Creative Commons CC0 1.0 Universal (Public Domain).

### 3. Library of Congress JSON/YAML API
- **ID:** `library_of_congress_api`
- **Canonical URL:** https://www.loc.gov/
- **Documentation:** https://www.loc.gov/apis/json-and-yaml/
- **API Status:** `documented_api`
- **Rate Limit Policy:** Standard polite access (10–20 requests/sec); no API key required for public endpoints.
- **Content Format:** JSON.
- **Role in KathaYantra:** American folklore collections, historical oral histories from the American Folklife Center, and Chronicling America historical press records.
- **Licensing:** Catalog metadata is public domain (CC0); digital items vary according to collection copyright. KathaYantra retains metadata and source links.

### 4. Internet Archive API & Metadata Service
- **ID:** `internet_archive`
- **Canonical URL:** https://archive.org/
- **Documentation:** https://archive.org/developers/
- **API Status:** `documented_api`
- **Rate Limit Policy:** Backoff required on HTTP 429 response codes; concurrent requests should be throttled.
- **Content Format:** JSON.
- **Role in KathaYantra:** Discovering 19th-century scanned folklore anthologies and public-domain myth collections.
- **Licensing:** Rights vary strictly by item. Hosting on Archive.org does not constitute public domain status. Items must be verified as pre-1929 publications before narrative ingestion.

### 5. Myths of Ireland Structured Dataset
- **ID:** `myths_of_ireland`
- **Canonical URL:** https://www.mythsofireland.com/
- **Documentation / Dataset:** https://www.mythsofireland.com/dataset/
- **API Status:** `public_dataset`
- **Content Format:** Downloadable JSON / CSV.
- **Role in KathaYantra:** Structured relational index of Irish mythological beings, places, stories, cycles, and relationships.
- **Licensing:** Creative Commons Attribution 4.0 International (CC BY 4.0) for the downloadable index dataset. Retellings on the website remain separate.

### 6. Nichibunken Yōkai Database
- **ID:** `nichibunken_yokai_db`
- **Canonical URL:** https://www.nichibun.ac.jp/en/db/category/yokai/
- **Documentation:** https://www.nichibun.ac.jp/ja/db/category/yokai/
- **API Status:** `searchable_catalogue`
- **Role in KathaYantra:** Academic provenance and scholarly citations for Japanese yōkai and supernatural folklore.
- **Licensing:** Institutional copyright held by the International Research Center for Japanese Studies. Used for bibliographic citations only.

### 7. Japan Search (NDL Cultural Heritage Platform)
- **ID:** `japan_search`
- **Canonical URL:** https://jpsearch.go.jp/
- **Documentation:** https://jpsearch.go.jp/static/developer/introduction/en.html
- **API Status:** `documented_api`
- **Content Format:** JSON-LD / SPARQL JSON.
- **Role in KathaYantra:** Japanese cultural heritage properties, digitized emakimono (scrolls), and folklore museum records.
- **Licensing:** Metadata is open government data; media objects carry provider-specific licenses.

### 8. Europeana Digital Heritage REST API
- **ID:** `europeana_api`
- **Canonical URL:** https://www.europeana.eu/
- **Documentation:** https://www.europeana.eu/en/apis
- **API Status:** `requires_credentials`
- **Authentication:** Free API key required (configured via `EUROPEANA_API_KEY` environment variable).
- **Rate Limit Policy:** 5 requests/sec.
- **Role in KathaYantra:** European folklore manuscripts and historical prints across Greece, Germany, Ireland, and the United Kingdom.
- **Licensing:** Metadata is CC0 1.0 Universal; media object rights are declared per item.

### 9. National Cultural Audiovisual Archives (NCAA) — India
- **ID:** `ncaa_india`
- **Canonical URL:** https://ncaa.gov.in/repository/
- **API Status:** `searchable_catalogue`
- **Role in KathaYantra:** Indian intangible cultural heritage, oral traditions, and tribal folklore documentation.
- **Licensing:** Ministry of Culture, Government of India; institutional repository rights reserved.

### 10. Dúchas — National Folklore Collection of Ireland
- **ID:** `duchas_ireland`
- **Canonical URL:** https://www.duchas.ie/en
- **Documentation:** https://docs.gaois.ie/en/data/duchas/v0.6/api
- **API Status:** `not_yet_verified`
- **Role in KathaYantra:** The Schools' Collection (1937–1938) and Irish folklore manuscripts.
- **Licensing:** CC BY-NC 4.0; non-commercial research use only. Legacy API endpoints require verification before integration.

### 11. Centro Nacional de Folclore e Cultura Popular (CNFCP / IPHAN) — Brazil
- **ID:** `cnfcp_iphan_brazil`
- **Canonical URL:** https://acervosdigitais.cnfcp.gov.br/AcervoFolclore
- **Documentation:** https://www.gov.br/iphan/pt-br/unidades-especiais/centro-nacional-de-folclore-e-cultura-popular
- **API Status:** `searchable_catalogue`
- **Role in KathaYantra:** Brazilian folklore books, cordel literature, and afro-indigenous oral tradition archives.
- **Licensing:** IPHAN institutional copyright; reference use only.

### 12. Project Gutenberg
- **ID:** `project_gutenberg`
- **Canonical URL:** https://www.gutenberg.org/
- **Robot Access Policy:** https://www.gutenberg.org/policy/robot_access.html
- **API Status:** `public_dataset`
- **Rate Limit Policy:** Max 1 request every 2 seconds; bulk access must use mirrors or catalog feeds.
- **Role in KathaYantra:** Pre-1929 public-domain folklore anthologies (e.g., Andrew Lang, Joseph Jacobs, Brothers Grimm translations, Lafcadio Hearn).
- **Licensing:** Public Domain in the United States. Project Gutenberg trademark headers must be stripped for redistributing the underlying public-domain text.

### 13. Urban Legends Online
- **ID:** `urban_legends_online`
- **Canonical URL:** https://urbanlegendsonline.com/
- **API Status:** `reference_only`
- **Role in KathaYantra:** Discovery reference for identifying modern urban legend motifs and rumors.
- **Licensing:** Modern retellings are copyrighted. Scraping and bulk copying are strictly prohibited; used solely as an archival discovery index.

### 14. Urban Legends Archive
- **ID:** `urban_legends_archive`
- **Canonical URL:** https://urbanlegendsarchive.com/list-of-urban-legends/
- **API Status:** `reference_only`
- **Role in KathaYantra:** Discovery reference for modern ghost stories and contemporary folklore.
- **Licensing:** Proprietary editorial retellings. Reference only.

### 15. Folklore-ai GitHub Repository
- **ID:** `folklore_ai_github`
- **Canonical URL:** https://github.com/AkshayGMys/Folklore-ai
- **API Status:** `reference_only`
- **Role in KathaYantra:** Technical and prompt architecture reference for Indian mythological narrative concepts.
- **Licensing:** Synthetic AI stories cannot be accepted as authentic historical folklore.

### 16. Business Insider World Urban Legends Survey
- **ID:** `business_insider_urban_legends`
- **Canonical URL:** https://www.businessinsider.com/urban-legends-from-around-the-world
- **API Status:** `reference_only`
- **Role in KathaYantra:** Journalistic secondary index highlighting prominent international urban legends.

### 17. Wikipedia Category: Urban legends by country
- **ID:** `wikipedia_urban_legends_category`
- **Canonical URL:** https://en.wikipedia.org/wiki/Category:Urban_legends_by_country
- **Documentation:** https://www.mediawiki.org/wiki/API:Categorymembers
- **API Status:** `documented_api`
- **Role in KathaYantra:** Programmatic category traversal for discovering documented urban legends across the 15 target nations.
- **Licensing:** CC BY-SA 4.0.

