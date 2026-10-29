# KathaYantra — Curatorial Guide & Editorial Governance Manual

> **Guiding Principle:** *Preserve the story. Trace the source. Respect the culture. Keep the AI honest.*

---

## 1. Executive Summary

**KathaYantra** is a local-first, open-source-AI-powered cultural heritage archive dedicated to cataloging and preserving world folklore and modern urban legends across 15 countries.

Every record published in the KathaYantra archive adheres to rigorous data governance standards:
- **Traceable Provenance:** Every narrative must cite verified, accessible bibliographic or institutional sources with valid HTTP/HTTPS URLs.
- **Original Summaries:** Summaries must be original synopses written specifically for KathaYantra to prevent verbatim copyright infringement and avoid synthetic AI artifacts.
- **Respectful Attribution:** Regional, ethnic, and cultural community associations must be honored and documented accurately.
- **Strict Anti-Hallucination Safeguards:** AI-generated creative fiction is segregated into `GeneratedFictionRecord` envelopes and strictly prohibited from entering canonical folklore datasets.

---

## 2. Core Curatorial Categorization

### A. Folklore (`folklore`)
Traditional oral narratives, myths, indigenous cosmologies, supernatural beings, regional fairy tales, and cultural traditions transmitted across generations.
- **Historical Era:** Traditional, pre-modern, or historical eras.
- **Verification Requirement:** Documented in academic anthologies, national library archives, folklore society publications, or reputable historical records.
- **Examples:**
  - *India:* The Vikram and Betal Cycle, The Legend of the Daayan.
  - *Japan:* The Tale of the Bamboo Cutter (Kaguya-hime), The Kappa of the Rivers.
  - *Ireland:* The Salmon of Knowledge (Fionn mac Cumhaill), The Banshee's Lament.
  - *Brazil:* Saci-Pererê, Curupira and the Sacred Forests.

### B. Urban Legends (`urban_legend`)
Contemporary folklore, circulating rumours, ghost encounters, modern schoolyard terrors, and digital mystery lore rooted in modern or contemporary settings.
- **Distinction from Fact:** An urban legend is **not** a verified historical event; it is an index of modern cultural anxiety, folklore, and collective storytelling.
- **Verification Requirement:** Documented in folklore scholarship (e.g. Jan Harold Brunvand), regional cultural publications, news archives, or historical civic registers.
- **Examples:**
  - *United States:* The Mothman of Point Pleasant, The Vanishing Hitchhiker.
  - *Japan:* Kuchisake-onna (The Slit-Mouthed Woman), Hanako-san of the Toilet.
  - *South Korea:* The Ghost of Jayuro Expressway, Electric Fan Death.
  - *Mexico:* La Llorona of Xochimilco, La Planchada of Hospital Juárez.

---

## 3. Curatorial Lifecycle & Pipeline

The KathaYantra data lifecycle transitions through five distinct phases:

```
[External Repositories & APIs]
         │ (Harvest / API Connectors)
         ▼
  [ImportCandidate] ── Staged in data/processed/candidates/*.jsonl
         │
         ▼
[Source & Rights Audit] ── SourceVerificationService
         │
         ├── Reject / Duplicate ──> CandidateDispositionEnum.REJECTED
         │
         ▼
[Editorial Review & Summary] ── SummaryBuilder & CurationService
         │
         ▼
[Publication Policy Gate] ── PublicationPolicy (10 deterministic rules)
         │
         ▼
   [StoryRecord] ── Persisted in data/seed/{folklore,urban_legends}/{country}.json
         │
         ▼
 [DatasetEnvelope 2.0.0] & Manifest Sync
```

### Stage 1: Candidate Ingestion
- Harvested through approved open-data connectors (`MediaWiki`, `Wikidata`, `Europeana`, `Library of Congress`, `Internet Archive`, `Myths of Ireland`, etc.).
- Staged into `ImportCandidate` envelopes with raw metadata, provenance flags, and `disposition = new_candidate`.
- Quarantined in `data/processed/candidates/`.

### Stage 2: Source Verification & Provenance Inspection
Evaluated via `SourceVerificationService`:
1. **URL Scheme Check:** Must use `http://` or `https://` with valid hostname.
2. **Attribution Clearance:** If the source requires attribution, explicit attribution text must be captured.
3. **Rights Assessment:** Classify licensing state (`approved`, `public_domain_verified`, `metadata_only`, `needs_rights_review`, or `restricted`).
4. **Community Specificity:** Verify regional or community association (e.g., *Yoruba*, *Gaelic Irish*, *Amazonian indigenous*).

### Stage 3: Original Summary Formulation
Curated via `SummaryBuilder`:
- **Word Count Boundaries:** Recommended 50–250 words; hard minimum 20 words; maximum 600 words.
- **Anti-Plagiarism Check:** Regex scanning for verbatim reproduction markers (e.g., `"all rights reserved"`, `"chapter 1:"`).
- **Anti-Hallucination Filter:** Automated rejection of AI filler phrases (e.g., `"as an ai"`, `"as a language model"`, `"todo: add story"`).
- **Narrative Arc:** Clear exposition of key figures, cultural setting, encounter/conflict, and symbolic significance.

### Stage 4: Publication Policy Gate
Evaluated against `PublicationPolicy.evaluate_eligibility(record)`:
1. Valid canonical identifier format (`{country_code}-{category}-{index:03d}`).
2. Valid country code among the 15 supported ISO codes.
3. Content origin is not synthetic fiction (`content_origin != ai_generated_fiction`).
4. Verification status is `verified` or approved review.
5. Rights status is `approved` or `public_domain_verified`.
6. At least one valid bibliographic source cited.
7. Summary meets minimum length and substance requirements.
8. Attribution obligations are fully satisfied.

### Stage 5: Envelope Packaging & Manifest Synchronisation
- Validated records are packaged into versioned `DatasetEnvelope` structures (`schema_version = 2.0.0`).
- Written to atomic JSON files under `data/seed/folklore/{country}.json` and `data/seed/urban_legends/{country}.json`.
- Global dataset manifest (`data/manifests/dataset_manifest.json`) is refreshed with actual counts, checksums, and source lists.

---

## 4. Archive Quota & Target Breakdown

KathaYantra maintains a strict, non-negotiable quota target:

$$\text{Total Target} = 15 \text{ Countries} \times (10 \text{ Folklore} + 10 \text{ Urban Legends}) = 300 \text{ Stories}$$

### Current Status: 100.0% Complete (300 / 300 Stories)

| ISO | Country | Folklore Target | Folklore Actual | Urban Legend Target | Urban Legend Actual | Status |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| `BR` | Brazil | 10 | 10 | 10 | 10 | **MET** |
| `CN` | China | 10 | 10 | 10 | 10 | **MET** |
| `DE` | Germany | 10 | 10 | 10 | 10 | **MET** |
| `EG` | Egypt | 10 | 10 | 10 | 10 | **MET** |
| `GB` | United Kingdom | 10 | 10 | 10 | 10 | **MET** |
| `GR` | Greece | 10 | 10 | 10 | 10 | **MET** |
| `ID` | Indonesia | 10 | 10 | 10 | 10 | **MET** |
| `IE` | Ireland | 10 | 10 | 10 | 10 | **MET** |
| `IN` | India | 10 | 10 | 10 | 10 | **MET** |
| `JP` | Japan | 10 | 10 | 10 | 10 | **MET** |
| `KR` | South Korea | 10 | 10 | 10 | 10 | **MET** |
| `MX` | Mexico | 10 | 10 | 10 | 10 | **MET** |
| `NG` | Nigeria | 10 | 10 | 10 | 10 | **MET** |
| `PH` | Philippines | 10 | 10 | 10 | 10 | **MET** |
| `US` | United States | 10 | 10 | 10 | 10 | **MET** |

---

## 5. Curatorial Tooling & Command Reference

### Check Archive Quotas & Deficits
```bash
python scripts/check_country_quotas.py
```
*Outputs a real-time terminal table detailing the completion status across all 15 countries and 30 partitions.*

To generate a Markdown report:
```bash
python scripts/check_country_quotas.py --markdown
```

### Build & Populate Verified Seed Datasets
```bash
python scripts/build_verified_dataset.py
```
*Validates all 300 curated story records against `PublicationPolicy`, writes seed envelopes into `data/seed/`, and updates `data/manifests/dataset_manifest.json`.*

To run in dry-run mode without disk writes:
```bash
python scripts/build_verified_dataset.py --dry-run
```

### Inspect & Review Staged Candidates
```bash
# List all pending candidates
python scripts/curate_candidate_records.py --list

# Filter by country
python scripts/curate_candidate_records.py --list --country IN

# Inspect candidate details
python scripts/curate_candidate_records.py --inspect CAND-FT-0001

# Approve candidate
python scripts/curate_candidate_records.py --approve CAND-FT-0001 --curator editor_1 --notes "Verified public domain source"

# Reject candidate
python scripts/curate_candidate_records.py --reject CAND-FT-0002 --curator editor_1 --notes "Fails provenance standards"
```

### Report Staged Curation Status
```bash
python scripts/report_curation_status.py
```

### Validate Dataset Integrity
```bash
python scripts/validate_json_datasets.py
```

### Validate Schema Migration Status
```bash
python scripts/migrate_seed_json.py --check
```

---

## 6. AI Ethics and Attribution Protocol

1. **No Synthetic Folklore:** KathaYantra's folklore and urban legend records must never be generated by artificial intelligence. AI models may be used solely as assistive retrieval agents or for generating explicit fictional adaptations segregated into `GeneratedFictionRecord`.
2. **Honoring Cultural Communities:** Cultural stories are living legacies of real communities. Attributions must reference specific ethnic, regional, or linguistic groups (e.g., *Yoruba*, *Tagalog*, *Mixtec*, *Bengali*, *Bavarian*) rather than generic labels.
3. **Attribution Preservation:** When a story or source specifies attribution conditions (e.g., CC-BY or academic citation), the attribution text must accompany the record in all rendered interfaces and API payloads.
