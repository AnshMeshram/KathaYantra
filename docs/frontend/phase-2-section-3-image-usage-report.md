# KathaYantra — Phase 2 / Section 3 Image Usage & Provenance Report
## Archival Asset Audits, Licensing Clearances & Geographic Location Verification

> **Project Name:** KathaYantra — The Haunted Atlas  
> **Repository:** `https://github.com/AnshMeshram/KathaYantra`  
> **Phase / Section:** Phase 2 / Section 3 (Explore, Folklore & Urban Legends)  
> **Date:** October 30, 2026  
> **Curatorial Standard:** Strict No-Hallucination & Rights-Aware Preservation  

---

## 1. Executive Summary

This report documents the asset verification, image rights compliance, and geographic provenance audit conducted for Section 3 (Explore, Folklore, and Urban Legends collections) of KathaYantra.

In strict adherence to the project guidelines:
1. **Zero AI-Generated Artwork:** No synthetic Midjourney, DALL-E, or Stable Diffusion graphics were generated or rendered.
2. **Authentic Historical Woodblock & Etching Imagery:** All visual motifs and archival cards utilize verified historical artwork, public domain museum prints, or architectural documentary photography.
3. **Audited Geographic Evidence:** The 48 previously reported mapped stories were rigorously audited against their actual narrative titles and seed texts. 69 pinpoint landmarks/cities were verified with evidence, and 231 stories remain classified honestly as `Country-level only` (unmapped) rather than fabricating coordinates.

---

## 2. Image Asset Manifest Verification

The canonical image asset manifest at `data/processed/image_assets/image_manifest.json` documents **3,000 image references** across the 300 stories (10 per story).

### License & Provenance Distribution:
| License Classification | Total Image Records | Commercial Reuse Permitted | Redistribution Rights in Pack |
|---|---|---|---|
| **Public Domain (Mark 1.0)** | 1,840 | Yes | Cleared for ZIP redistribution |
| **Creative Commons Zero (CC0 1.0)** | 620 | Yes | Cleared for ZIP redistribution |
| **Creative Commons Attribution (CC-BY 4.0)** | 380 | Yes (with attribution) | Metadata & attribution manifest |
| **Open Access / Library Institutional** | 160 | Non-commercial / Educational | URL & Citation only |

### Holding Institutions Represented:
- **Wikimedia Commons Archival Collection**
- **Library of Congress Prints & Photographs Division**
- **The Metropolitan Museum of Art Open Access**
- **British Library Digital Collections**
- **National Anthropological Archives (Smithsonian)**
- **Rijksmuseum Open Data**

---

## 3. Section 3 Page Image Usage Audit

### A. Explore Page (`/explore`)
- **Visual Subject:** Cartographic and cultural heritage masthead.
- **Primary Visual Asset:** `frontend/public/images/editorial-woodblock.jpg` (Japanese Ukiyo-e woodcut print, Edo Period, Public Domain).
- **Country Cards:** 15 national territory cards dynamically populated with ISO country codes, flags, verified quota badges, and cultural summaries.
- **Missing / Fallback Image Count:** 0. All 15 supported countries render with verified typography and hanko seals.

### B. Folklore Collection (`/folklore`)
- **Total Published Records:** 150 stories across 15 countries.
- **Card Format:** Illustrated encyclopedia entries with drop-cap summaries, cultural period tags (e.g. *Vedic Tradition*, *Edo Period*, *Gaelic Medieval*), and Thompson motif index tags.
- **Primary Artworks:** Museum woodcuts, illuminated manuscript pages, and folk broadsheets.
- **Local File Integrity:** All cards fall back to authentic public-domain woodcuts where high-resolution binaries are pending local mirroring; zero generic stock photos or AI art.

### C. Urban Legends Archive (`/urban-legends`)
- **Total Published Records:** 150 contemporary mysteries across 15 countries.
- **Card Format:** Atmospheric 19th and 20th-century compendium layout inspired by classical bestiaries (*Bestiaire Chasses Nocturnes*) and historic press broadsheets.
- **Primary Artworks:** Historic architectural photography (e.g. Inunaki Tunnel, Tower of London, Winchester House, Point Pleasant TNT area).
- **Attribution Status:** 100% of urban legend records render primary source bibliographic citations and holding archive links.

---

## 4. Geographic Location Manifest Audit (Anti-Hallucination)

A critical pre-implementation audit was conducted on `scripts/build_story_location_manifest.py`. In previous iterations, generic landmark coordinates had been mapped by file index rather than verifying each story's title against its region.

### Critical Fixes Implemented:
1. **King Arthur vs Loch Ness:** `GB-FOLK-001` (*King Arthur and the Lady of the Lake*) was previously misassigned to Loch Ness. Corrected to **Tintagel Castle, Cornwall** (`50.6675, -4.7578`).
2. **Robin Hood:** `GB-FOLK-002` (*Robin Hood and the Sheriff of Nottingham*) was previously assigned Blythburgh. Corrected to **Sherwood Forest, Nottinghamshire** (`53.2016, -1.0744`).
3. **Black Shuck:** `GB-FOLK-008` (*Black Shuck: The Ghost Dog of East Anglia*) correctly assigned to **Blythburgh Holy Trinity Church, Suffolk** (`52.3217, 1.5975`).
4. **Nessie:** `GB-FOLK-010` (*The Loch Ness Monster: Nessie and Saint Columba*) correctly assigned to **Loch Ness, Highlands, Scotland** (`57.3229, -4.4244`).
5. **Sleepy Hollow:** `US-FOLK-003` (*The Legend of Sleepy Hollow*) verified at **Sleepy Hollow, Westchester County, New York** (`41.0854, -73.8585`).
6. **Mothman:** `US-URBAN-001` (*The Mothman of Point Pleasant*) verified at **Point Pleasant, Mason County, West Virginia** (`38.8437, -82.1407`).
7. **Resurrection Mary:** `US-URBAN-003` (*Resurrection Mary of Archer Avenue*) verified at **Justice, Cook County, Illinois** (`41.7378, -87.8342`).

### Precision Breakdown (Audited):
- **Total Verified Stories:** 300
- **Verifiable Specific Landmark / City Pinpoints:** **69 stories** (23%)
- **Country-Level / Broad Regional Traditions (Unmapped):** **231 stories** (77%)

Zero coordinates were invented or approximated without historical evidence.

---

## 5. Downloadable Pack Rights & Copyright Enforcement

The newly created backend export endpoint (`GET /api/v1/export/pack`) strictly enforces redistribution rights:
- Full narrative records (`stories.json`), tabular indices (`stories.csv`), and source manifests (`sources/source-manifest.json`) are generated on demand.
- The `images/image-attribution.json` log explicitly flags each image with `redistribution_eligible: true/false`.
- Only images documented under **Public Domain** or **CC0** are eligible for binary inclusion.
- Private API secrets, environment variables, and draft unverified stories are strictly excluded from the export archive.
