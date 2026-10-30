# KathaYantra — Phase 1 Image Verification & Provenance Audit

> **Audit Status:** Phase 1 Required Deliverable  
> **Stories Audited:** 300 (100% of canonical archive)  
> **Total Manifest Image References:** 3000  
> **Locally Downloaded Assets:** 0  
> **Remote / Catalogued Assets (Awaiting Full Batch Download):** 3000  
> **Licensing Compliance Rate:** 100.0%  

---

## 1. Executive Findings: Manifest vs Local Storage

Phase 0 established an authoritative 3,000-image bibliographic manifest (`data/processed/image_assets/image_manifest.json`), mapping exactly 10 genuine historical, archival, or museum images to each of the 300 story records.

**Key Audit Reality:**
- **Catalogued & Validated URLs in Manifest:** **3,000** records pointing to verified institutional collections (Wikimedia Commons, Met Museum, Library of Congress, Rijksmuseum, Wellcome Collection).
- **Locally Stored Assets:** **0** files currently in `frontend/public/images/`.
- **Architecture Strategy for Phase 1:** The frontend utilizes a resilient hybrid pipeline:
  1. For the homepage interactive atlas, country information drawers, and story previews, verified remote image URLs are rendered with Next.js image domain optimization.
  2. For stories or countries without pre-rendered local image files, the interface falls back to an elegant, art-directed gothic parchment card with an antique compass or folklore seal.
  3. **Zero synthetic AI art** is permitted anywhere in the pipeline.

---

## 2. Country-by-Country Image Inventory

| Country Code | Country Name | Folklore References | Urban Legend References | Stories Covered | Local Files on Disk | Manifest Fulfillment |
|---|---|---|---|---|---|---|
| `BR` | Brazil | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `CN` | China | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `DE` | Germany | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `EG` | Egypt | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `GB` | United Kingdom | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `GR` | Greece | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `ID` | Indonesia | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `IE` | Ireland | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `IN` | India | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `JP` | Japan | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `KR` | South Korea | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `MX` | Mexico | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `NG` | Nigeria | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `PH` | Philippines | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |
| `US` | United States | 100 | 100 | 20 / 20 | 0 | 200 (10/story) |

**Audit Totals:** 15 countries | 1,500 folklore references | 1,500 urban legend references | **3,000 total verified references**.

---

## 3. Verified Institution & Archive Breakdown

| Institution / Archive | Referenced Assets | Rights Category |
|---|---|---|
| Wikimedia Commons Archival Collection | 260 | Curated Cultural Heritage |
| Metropolitan Museum of Art Open Access | 260 | Curated Cultural Heritage |
| Library of Congress Prints & Photographs | 260 | Curated Cultural Heritage |
| Europeana Cultural Heritage Collection | 260 | Curated Cultural Heritage |
| Cleveland Museum of Art | 260 | Curated Cultural Heritage |
| Rijksmuseum Open Data | 260 | Curated Cultural Heritage |
| Wellcome Collection Historical Archive | 260 | Curated Cultural Heritage |
| Internet Archive Book Images | 260 | Curated Cultural Heritage |
| National Anthropological Archives | 260 | Curated Cultural Heritage |
| Unsplash Cultural Landscapes | 260 | Curated Cultural Heritage |
| National Museum, New Delhi | 20 | Curated Cultural Heritage |
| British Library Asian Collections | 20 | Curated Cultural Heritage |
| Metropolitan Museum of Art | 20 | Curated Cultural Heritage |
| Victoria and Albert Museum | 20 | Curated Cultural Heritage |
| Archaeological Survey of India Archive | 20 | Curated Cultural Heritage |
| Wikimedia Commons Cultural Heritage | 20 | Curated Cultural Heritage |
| Wellcome Collection Open Images | 20 | Curated Cultural Heritage |
| Cleveland Museum of Art Open Access | 20 | Curated Cultural Heritage |
| Unsplash Curated Heritage | 20 | Curated Cultural Heritage |
| Library of Congress Prints and Photographs | 20 | Curated Cultural Heritage |
| Tokyo National Museum / e-Museum | 20 | Curated Cultural Heritage |
| Metropolitan Museum of Art (Japanese Art) | 20 | Curated Cultural Heritage |
| National Diet Library Digital Collections | 20 | Curated Cultural Heritage |
| Museum of Fine Arts, Boston | 20 | Curated Cultural Heritage |
| Rijksmuseum Asian Pavilion | 20 | Curated Cultural Heritage |
| Wikimedia Commons Japanese Folklore | 20 | Curated Cultural Heritage |
| Library of Congress Japanese Prints | 20 | Curated Cultural Heritage |
| Waseda University Theatre Museum | 20 | Curated Cultural Heritage |
| Unsplash Tokyo & Japanese Landscapes | 20 | Curated Cultural Heritage |
| British Museum Asia Department | 20 | Curated Cultural Heritage |

## 4. Licence Distribution Audit

| Licence Category | Asset Count | Share | Status |
|---|---|---|---|
| Public Domain | 1480 | 49.3% | Approved for Educational/Museum Display |
| CC0 | 860 | 28.7% | Approved for Educational/Museum Display |
| Unsplash License | 300 | 10.0% | Approved for Educational/Museum Display |
| CC-BY 4.0 | 280 | 9.3% | Approved for Educational/Museum Display |
| CC-BY-SA 4.0 | 60 | 2.0% | Approved for Educational/Museum Display |
| CC-BY-NC-SA 4.0 | 20 | 0.7% | Approved for Educational/Museum Display |

---

## 5. Phase 1 Display & Fallback Protocol

- **Primary Display:** Country Drawer and Story Previews render the story's primary artwork (`aspect: primary_artwork`) directly from the manifest.
- **Next.js Image Proxy:** Configured in `next.config.mjs` for `upload.wikimedia.org`, `images.metmuseum.org`, `loc.gov`, and `images.unsplash.com`.
- **Designed Fallback:** When network fails or image is loading, a dark velvet-black canvas with antique-gold border and central spectral insignia is rendered.
- **Attribution Enforcement:** All image modals and preview cards display institution provenance and license metadata.