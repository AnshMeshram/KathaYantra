# Folk Tales Dataset Audit Report

**Audited Asset:** `folk_tales_deduplicated.csv`  
**File Size:** 27,240,952 bytes (25.98 MB)  
**Total Records:** 2,938  
**Audit Status:** Completed — `needs_rights_review`  

---

## 1. Executive Summary

An automated, deterministic audit of `folk_tales_deduplicated.csv` was conducted. The file contains **2,938 records** across 4 columns: `source`, `nation`, `title`, and `text`.

While originally titled "deduplicated", the audit identified:
- **3 pairs (6 rows) of exact identical text duplicates**.
- **15 pairs of near-duplicate story texts** (differing primarily by typography, smart quotes, character encoding, or minor editorial prefixes).
- **42 recurring story titles** spanning 85 total rows.
- **6 rows with completely missing nation values**.
- Over **98.8% of URLs** originate from a single commercial storytelling website (`fairytalez.com`).

**Crucial Rights Conclusion:** The presence of publicly reachable URLs does not grant redistribution rights for full-text stories. The raw dataset must be retained strictly as a restricted research artifact and must **not** be published in KathaYantra's seed corpus or public API without individual rights clearance or original re-summarization.

---

## 2. Column and Data Completeness

| Column | Missing Count | Status | Notes |
|---|---|---|---|
| `source` | 0 | Valid | 100% complete. All 2,938 URLs parse with valid schemes. |
| `nation` | 6 | **Action Required** | Exactly 6 rows lack a nation label. |
| `title` | 0 | Valid | 100% complete (2,894 unique titles). |
| `text` | 0 | Valid | 100% complete. No empty story texts. |

### Records Missing Nation Labels

The following 6 rows require manual archival provenance before any country assignment can occur:

| Row Index | Title | Source URL |
|---|---|---|
| 1290 | The Seven Stages of Roostem | [https://fairytalez.com/seven-stages-roostem/](https://fairytalez.com/seven-stages-roostem/) |
| 1326 | The Doomed Prince | [https://fairytalez.com/the-doomed-prince/](https://fairytalez.com/the-doomed-prince/) |
| 1687 | The Fairy in the Cuckoo Clock | [https://fairytalez.com/the-fairy-in-the-cuckoo-clock/](https://fairytalez.com/the-fairy-in-the-cuckoo-clock/) |
| 1773 | The Greedy Old Man | [https://fairytalez.com/the-greedy-old-man/](https://fairytalez.com/the-greedy-old-man/) |
| 2046 | The Story Of The Sham Prince, Or The Ambitious Tailor | [https://fairytalez.com/story-sham-prince-ambitious-tailor/](https://fairytalez.com/story-sham-prince-ambitious-tailor/) |
| 2430 | The Prince and the Three Fates | [https://fairytalez.com/the-prince-and-the-three-fates/](https://fairytalez.com/the-prince-and-the-three-fates/) |

---

## 3. Nation & Cultural Distribution

The raw dataset spans **58 distinct nation values** (including the blank entry). Below are the top 25 nations represented:

| Raw Nation Label | Record Count | Percentage |
|---|---|---|
| `north_american_native` | 370 | 12.59% |
| `greek` | 304 | 10.35% |
| `german` | 277 | 9.43% |
| `french` | 168 | 5.72% |
| `indian` | 130 | 4.42% |
| `english` | 120 | 4.08% |
| `italian` | 105 | 3.57% |
| `chinese` | 101 | 3.44% |
| `japanese` | 88 | 3.0% |
| `nordic` | 85 | 2.89% |
| `russian` | 80 | 2.72% |
| `philippine` | 73 | 2.48% |
| `scandinavian` | 72 | 2.45% |
| `irish` | 60 | 2.04% |
| `portuguese` | 55 | 1.87% |
| `danish` | 51 | 1.74% |
| `australian_ethnic` | 49 | 1.67% |
| `czechoslovak` | 46 | 1.57% |
| `slavic` | 44 | 1.5% |
| `scottish` | 43 | 1.46% |
| `arabic` | 41 | 1.4% |
| `celtic` | 40 | 1.36% |
| `nigerian` | 39 | 1.33% |
| `armenian` | 31 | 1.06% |
| `brazilian` | 31 | 1.06% |

### Critical Mapping Observations:
1. **Indigenous Representation:** The largest single label is `north_american_native` (370 tales). This label merges hundreds of distinct sovereign Indigenous Nations across North America (e.g. Ojibwe, Cherokee, Haida, Hopi) and cannot be generalized into modern "US" folklore.
2. **Target Country Overlap:** Only a subset of labels map cleanly to KathaYantra's 15 target countries (`indian` -> IN: 130, `greek` -> GR: 304, `german` -> DE: 277, `chinese` -> CN: 101, `japanese` -> JP: 88, `philippine` -> PH: 73, `irish` -> IE: 60, `brazilian` -> BR: 55, `korean` -> KR: 21, `nigerian` -> NG: 15).
3. **Missing Target Countries:** Several target countries have zero representation in this CSV, notably **Mexico (MX)**, **Egypt (EG)**, and **Indonesia (ID)**. Additional dedicated sources must be integrated in future phases.

---

## 4. Source Domains and URL Health

| Domain | Record Count | Share |
|---|---|---|
| `fairytalez.com` | 2903 | 98.81% |
| `www.albanianliterature.net` | 25 | 0.85% |
| `www.worldoftales.com` | 10 | 0.34% |

- **Malformed URLs Detected:** 0
- **Unique URLs:** 2,938 of 2,938 rows.

---

## 5. Duplicate and Near-Duplicate Analysis

### Exact Duplicate Texts (3 pairs found)
- **Rows [421, 2797]**: Title: *The Weeoonibeens and the Piggiebillah* (Nation: `australian_ethnic`) — 6477 chars
- **Rows [1455, 2317]**: Title: *The Passing of Loku* (Nation: `philippine`) — 2005 chars
- **Rows [2544, 2816]**: Title: *The Three Sisters* (Nation: `italian`) — 10102 chars

### Near-Duplicate Texts (15 pairs identified)
Near duplicates were identified using normalized prefix-suffix signature hashing and token Jaccard similarity (>= 0.85):
- **Rows [177, 1681]** (`same_title_high_jaccard`): *The Farmer and the Money-Lender* (`indian`) vs *The Farmer and the Money-Lender* (`indian`) — Jaccard: 0.9618
- **Rows [205, 916]** (`same_title_high_jaccard`): *Black Bull of Norroway* (`scottish`) vs *Black Bull of Norroway* (`english`) — Jaccard: 0.9659
- **Rows [300, 1182]** (`normalized_prefix_suffix_signature`): *The Magic Ring* (`english`) vs *The Magic Ring* (`english`) — Jaccard: 1.0
- **Rows [304, 1281]** (`same_title_high_jaccard`): *The Tiger, the Brahman and the Jackal* (`indian`) vs *The Tiger, the Brahman and the Jackal* (`indian`) — Jaccard: 0.9638
- **Rows [421, 2797]** (`normalized_prefix_suffix_signature`): *The Weeoonibeens and the Piggiebillah* (`australian_ethnic`) vs *The Weeoonibeens and the Piggiebillah* (`australian_ethnic`) — Jaccard: 1.0
- **Rows [451, 1109]** (`normalized_prefix_suffix_signature`): *Wise Folks* (`german`) vs *Wise Folks* (`german`) — Jaccard: 0.9977
- **Rows [883, 2231]** (`normalized_prefix_suffix_signature`): *The Three Brothers* (`serbian`) vs *The Wonderful Bird* (`serbian`) — Jaccard: 1.0
- **Rows [1038, 1082]** (`same_title_high_jaccard`): *The Old Woman in the Wood* (`german`) vs *The Old Woman in the Wood* (`german`) — Jaccard: 0.9934
- **Rows [1173, 2507]** (`normalized_prefix_suffix_signature`): *The Priest's Supper* (`irish`) vs *The Priest* (`irish`) — Jaccard: 0.9978
- **Rows [1384, 2785]** (`normalized_prefix_suffix_signature`): *The Lambikin* (`indian`) vs *The Lambikin* (`indian`) — Jaccard: 0.9369
- **Rows [1455, 2317]** (`normalized_prefix_suffix_signature`): *The Passing of Loku* (`philippine`) vs *The Passing of Loku* (`philippine`) — Jaccard: 1.0
- **Rows [1522, 2652]** (`same_title_high_jaccard`): *The Tobacco of Harisaboqued* (`philippine`) vs *The Tobacco of Harisaboqued* (`philippine`) — Jaccard: 0.9913
- **Rows [1598, 2253]** (`normalized_prefix_suffix_signature`): *The Dragon's Tail* (`german`) vs *The Dragon's Tail* (`german`) — Jaccard: 1.0
- **Rows [2212, 2457]** (`normalized_prefix_suffix_signature`): *Fitcher's Bird* (`german`) vs *Fitcher's Bird* (`german`) — Jaccard: 0.9636
- **Rows [2544, 2816]** (`normalized_prefix_suffix_signature`): *The Three Sisters* (`italian`) vs *The Three Sisters* (`italian`) — Jaccard: 1.0

---

## 6. Text Length & Characteristics

- **Minimum Length:** 130 characters (20 words)
- **Maximum Length:** 106,121 characters (19,215 words)
- **Average Length:** 9,030.47 characters (~1,690.1 words)
- **Short Texts (< 50 words):** 6 records (brief fables, fragments).
- **Long Texts (> 15,000 words):** 1 record (novella-length fairy tale *The Ice Maiden*).

---

## 7. Rights, Provenance & Ingestion Safeguards

- 2,903 of 2,938 records (98.8%) originate from fairytalez.com, which retains copyright over its site presentation and editorial adaptations.
- 25 records originate from albanianliterature.net (Robert Elsie collection) with specific translation/editorial copyright.
- 10 records originate from worldoftales.com with site-specific compilation copyright.
- Underlying folk tales are traditional cultural heritage, but specific English translations, editorial adaptations, and digital compilations cannot be presumed public domain without source anthology verification.
- Public web accessibility does NOT grant license to redistribute full story bodies in KathaYantra's published dataset or public API.
- Recommendation: Treat raw CSV as restricted research input. Ingest only bibliographic metadata and write original verified summaries for published archive entries.

### Phase 1 Archival Directives:
1. Store raw CSV in `data/raw/folk_tales_deduplicated.csv` with gitignore protection against public repository publication.
2. Mark all raw records with `rights_status: needs_rights_review`.
3. Do not import full-text into `data/seed/` or public API responses.
4. Prepare clean schemas for verified original summaries and citations.
