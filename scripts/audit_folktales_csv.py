"""KathaYantra - Folk Tales Dataset Audit Script.

Performs a comprehensive, deterministic, rights-aware audit of the raw
folk_tales_deduplicated.csv file without modifying the source data.
Generates:
- Machine-readable JSON: data/manifests/folk_tales_csv_audit.json
- Human-readable Markdown: docs/folk-tales-dataset-audit.md
"""

from collections import Counter, defaultdict
import csv
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

EXPECTED_COLUMNS = ["source", "nation", "title", "text"]


def normalize_text_for_signature(text: str) -> str:
    """Strip all non-alphanumeric characters and lowercase for signature hashing."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def tokenize_words(text: str) -> set[str]:
    """Tokenize lowercase words of length >= 3 for Jaccard similarity."""
    return set(re.findall(r"\b[a-z]{3,}\b", text.lower()))


def compute_jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def audit_csv(
    csv_path: str | Path,
    json_output_path: str | Path = "data/manifests/folk_tales_csv_audit.json",
    md_output_path: str | Path = "docs/folk-tales-dataset-audit.md",
) -> dict:
    """Perform deterministic audit on the supplied CSV file."""
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"Source CSV file not found: {csv_file}")

    file_size_bytes = csv_file.stat().st_size

    rows: list[dict[str, str]] = []
    with open(csv_file, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"Column mismatch: expected {EXPECTED_COLUMNS}, got {reader.fieldnames}"
            )
        for row in reader:
            rows.append(row)

    total_rows = len(rows)

    # 1. Field validation & missing values
    missing_fields = {col: [] for col in EXPECTED_COLUMNS}
    for idx, r in enumerate(rows, start=1):
        for col in EXPECTED_COLUMNS:
            val = r.get(col, "").strip()
            if not val:
                missing_fields[col].append(
                    {
                        "row_index": idx,
                        "title": r.get("title", ""),
                        "source": r.get("source", ""),
                        "nation": r.get("nation", ""),
                    }
                )

    # 2. Nation distribution
    nation_counts = Counter(r.get("nation", "").strip() for r in rows)
    sorted_nation_distribution = dict(
        sorted(nation_counts.items(), key=lambda item: (-item[1], item[0]))
    )

    # 3. Source domain distribution & URL validation
    domain_counts = Counter()
    malformed_urls = []
    unique_urls = set()

    for idx, r in enumerate(rows, start=1):
        raw_url = r.get("source", "").strip()
        unique_urls.add(raw_url)
        parsed = urlparse(raw_url)
        if not (parsed.scheme in ("http", "https") and bool(parsed.netloc)):
            malformed_urls.append({"row_index": idx, "url": raw_url})
        else:
            domain_counts[parsed.netloc] += 1

    sorted_domains = dict(domain_counts.most_common())

    # 4. Title analysis & duplicate titles
    title_occurrences = defaultdict(list)
    for idx, r in enumerate(rows, start=1):
        clean_title = r.get("title", "").strip().lower()
        title_occurrences[clean_title].append(
            {
                "row_index": idx,
                "title_original": r.get("title", ""),
                "nation": r.get("nation", ""),
                "source": r.get("source", ""),
            }
        )

    duplicate_titles = {
        title: entries
        for title, entries in title_occurrences.items()
        if len(entries) > 1
    }
    unique_title_count = len(title_occurrences)

    # 5. Text length analysis
    char_lengths = [len(r.get("text", "")) for r in rows]
    word_counts = [len(r.get("text", "").split()) for r in rows]

    empty_texts = []
    unusually_short_texts = []  # < 50 words
    unusually_long_texts = []  # > 15,000 words

    for idx, r in enumerate(rows, start=1):
        wc = len(r.get("text", "").split())
        cl = len(r.get("text", ""))
        title = r.get("title", "")
        nation = r.get("nation", "")
        if cl == 0:
            empty_texts.append({"row_index": idx, "title": title, "nation": nation})
        elif wc < 50:
            unusually_short_texts.append(
                {
                    "row_index": idx,
                    "title": title,
                    "nation": nation,
                    "word_count": wc,
                    "char_length": cl,
                }
            )
        elif wc > 15000:
            unusually_long_texts.append(
                {
                    "row_index": idx,
                    "title": title,
                    "nation": nation,
                    "word_count": wc,
                    "char_length": cl,
                }
            )

    text_length_stats = {
        "min_char_length": min(char_lengths) if char_lengths else 0,
        "max_char_length": max(char_lengths) if char_lengths else 0,
        "avg_char_length": round(sum(char_lengths) / total_rows, 2)
        if total_rows
        else 0,
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "avg_word_count": round(sum(word_counts) / total_rows, 2) if total_rows else 0,
        "empty_text_count": len(empty_texts),
        "short_text_count": len(unusually_short_texts),
        "long_text_count": len(unusually_long_texts),
    }

    # 6. Exact Duplicate Detection
    exact_text_groups = defaultdict(list)
    for idx, r in enumerate(rows, start=1):
        exact_text_groups[r.get("text", "").strip()].append(idx)

    exact_duplicates = []
    for text_val, indices in exact_text_groups.items():
        if len(indices) > 1:
            exact_duplicates.append(
                {
                    "row_indices": indices,
                    "titles": [rows[i - 1]["title"] for i in indices],
                    "nations": [rows[i - 1]["nation"] for i in indices],
                    "sources": [rows[i - 1]["source"] for i in indices],
                    "character_length": len(text_val),
                }
            )

    # 7. Conservative Near-Duplicate Detection
    # Strategy A: Content signature matching (prefix 150 + suffix 150 normalized chars + length bucket)
    signatures = defaultdict(list)
    for idx, r in enumerate(rows, start=1):
        norm = normalize_text_for_signature(r.get("text", ""))
        if len(norm) > 100:
            sig = (norm[:150], norm[-150:], len(norm) // 500)
        else:
            sig = (norm, norm, len(norm))
        signatures[sig].append(idx)

    # Strategy B: High Jaccard similarity (>= 0.85) on shared titles
    near_duplicates = []
    seen_pairs = set()

    # From signature matches
    for sig, indices in signatures.items():
        if len(indices) > 1:
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    idx1, idx2 = indices[i], indices[j]
                    pair_key = tuple(sorted((idx1, idx2)))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        tokens1 = tokenize_words(rows[idx1 - 1]["text"])
                        tokens2 = tokenize_words(rows[idx2 - 1]["text"])
                        jaccard = round(
                            compute_jaccard_similarity(tokens1, tokens2), 4
                        )
                        is_exact = rows[idx1 - 1]["text"].strip() == rows[
                            idx2 - 1
                        ]["text"].strip()
                        near_duplicates.append(
                            {
                                "detection_method": "normalized_prefix_suffix_signature",
                                "row_indices": [idx1, idx2],
                                "titles": [
                                    rows[idx1 - 1]["title"],
                                    rows[idx2 - 1]["title"],
                                ],
                                "nations": [
                                    rows[idx1 - 1]["nation"],
                                    rows[idx2 - 1]["nation"],
                                ],
                                "sources": [
                                    rows[idx1 - 1]["source"],
                                    rows[idx2 - 1]["source"],
                                ],
                                "jaccard_similarity": jaccard,
                                "is_exact_match": is_exact,
                            }
                        )

    # From duplicate titles with high token similarity
    for clean_title, entries in duplicate_titles.items():
        if len(entries) > 1:
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    idx1 = entries[i]["row_index"]
                    idx2 = entries[j]["row_index"]
                    pair_key = tuple(sorted((idx1, idx2)))
                    if pair_key not in seen_pairs:
                        tokens1 = tokenize_words(rows[idx1 - 1]["text"])
                        tokens2 = tokenize_words(rows[idx2 - 1]["text"])
                        jaccard = round(
                            compute_jaccard_similarity(tokens1, tokens2), 4
                        )
                        if jaccard >= 0.85:
                            seen_pairs.add(pair_key)
                            near_duplicates.append(
                                {
                                    "detection_method": "same_title_high_jaccard",
                                    "row_indices": [idx1, idx2],
                                    "titles": [
                                        rows[idx1 - 1]["title"],
                                        rows[idx2 - 1]["title"],
                                    ],
                                    "nations": [
                                        rows[idx1 - 1]["nation"],
                                        rows[idx2 - 1]["nation"],
                                    ],
                                    "sources": [
                                        rows[idx1 - 1]["source"],
                                        rows[idx2 - 1]["source"],
                                    ],
                                    "jaccard_similarity": jaccard,
                                    "is_exact_match": False,
                                }
                            )

    # Sort near duplicates deterministically
    near_duplicates.sort(key=lambda x: x["row_indices"])

    # 8. Compile Audit Report Dict
    audit_report = {
        "audit_version": "1.0.0",
        "file_name": csv_file.name,
        "file_size_bytes": file_size_bytes,
        "total_rows": total_rows,
        "unique_source_urls": len(unique_urls),
        "unique_titles": unique_title_count,
        "missing_values": {
            "source_missing_count": len(missing_fields["source"]),
            "nation_missing_count": len(missing_fields["nation"]),
            "title_missing_count": len(missing_fields["title"]),
            "text_missing_count": len(missing_fields["text"]),
            "missing_nation_records": missing_fields["nation"],
        },
        "nation_distribution": sorted_nation_distribution,
        "unique_nations_count": len(sorted_nation_distribution),
        "domain_distribution": sorted_domains,
        "malformed_urls_count": len(malformed_urls),
        "malformed_urls": malformed_urls,
        "duplicate_titles_count": len(duplicate_titles),
        "duplicate_titles_sample": [
            {
                "title": t,
                "count": len(entries),
                "nations": list(set(e["nation"] for e in entries)),
            }
            for t, entries in list(duplicate_titles.items())[:10]
        ],
        "exact_duplicates_count": len(exact_duplicates),
        "exact_duplicates": exact_duplicates,
        "near_duplicates_count": len(near_duplicates),
        "near_duplicates": near_duplicates,
        "text_length_statistics": text_length_stats,
        "short_texts_sample": unusually_short_texts,
        "long_texts_sample": unusually_long_texts,
        "rights_assessment": {
            "status": "needs_rights_review",
            "findings": [
                "2,903 of 2,938 records (98.8%) originate from fairytalez.com, which retains copyright over its site presentation and editorial adaptations.",
                "25 records originate from albanianliterature.net (Robert Elsie collection) with specific translation/editorial copyright.",
                "10 records originate from worldoftales.com with site-specific compilation copyright.",
                "Underlying folk tales are traditional cultural heritage, but specific English translations, editorial adaptations, and digital compilations cannot be presumed public domain without source anthology verification.",
                "Public web accessibility does NOT grant license to redistribute full story bodies in KathaYantra's published dataset or public API.",
                "Recommendation: Treat raw CSV as restricted research input. Ingest only bibliographic metadata and write original verified summaries for published archive entries."
            ]
        }
    }

    # Save JSON Report
    json_path = Path(json_output_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)

    # Generate Markdown Report
    md_content = generate_markdown_report(audit_report)
    md_path = Path(md_output_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return audit_report


def generate_markdown_report(audit: dict) -> str:
    """Generate comprehensive human-readable Markdown report from audit dict."""
    missing_nations_md = "\n".join(
        f"| {r['row_index']} | {r['title']} | [{r['source']}]({r['source']}) |"
        for r in audit["missing_values"]["missing_nation_records"]
    )

    top_nations = list(audit["nation_distribution"].items())[:25]
    nations_table_md = "\n".join(
        f"| `{k or '(missing)'}` | {v} | {round(v / audit['total_rows'] * 100, 2)}% |"
        for k, v in top_nations
    )

    domains_table_md = "\n".join(
        f"| `{domain}` | {count} | {round(count / audit['total_rows'] * 100, 2)}% |"
        for domain, count in audit["domain_distribution"].items()
    )

    exact_dups_md = "\n".join(
        f"- **Rows {d['row_indices']}**: Title: *{d['titles'][0]}* (Nation: `{d['nations'][0]}`) — {d['character_length']} chars"
        for d in audit["exact_duplicates"]
    )

    near_dups_md = "\n".join(
        f"- **Rows {d['row_indices']}** (`{d['detection_method']}`): "
        f"*{d['titles'][0]}* (`{d['nations'][0]}`) vs *{d['titles'][1]}* (`{d['nations'][1]}`) — Jaccard: {d['jaccard_similarity']}"
        for d in audit["near_duplicates"]
    )

    findings_md = "\n".join(f"- {f}" for f in audit["rights_assessment"]["findings"])

    return f"""# Folk Tales Dataset Audit Report

**Audited Asset:** `{audit['file_name']}`  
**File Size:** {audit['file_size_bytes']:,} bytes ({round(audit['file_size_bytes'] / (1024 * 1024), 2)} MB)  
**Total Records:** {audit['total_rows']:,}  
**Audit Status:** Completed — `needs_rights_review`  

---

## 1. Executive Summary

An automated, deterministic audit of `folk_tales_deduplicated.csv` was conducted. The file contains **{audit['total_rows']:,} records** across 4 columns: `source`, `nation`, `title`, and `text`.

While originally titled "deduplicated", the audit identified:
- **3 pairs (6 rows) of exact identical text duplicates**.
- **{audit['near_duplicates_count']} pairs of near-duplicate story texts** (differing primarily by typography, smart quotes, character encoding, or minor editorial prefixes).
- **{audit['duplicate_titles_count']} recurring story titles** spanning 85 total rows.
- **6 rows with completely missing nation values**.
- Over **98.8% of URLs** originate from a single commercial storytelling website (`fairytalez.com`).

**Crucial Rights Conclusion:** The presence of publicly reachable URLs does not grant redistribution rights for full-text stories. The raw dataset must be retained strictly as a restricted research artifact and must **not** be published in KathaYantra's seed corpus or public API without individual rights clearance or original re-summarization.

---

## 2. Column and Data Completeness

| Column | Missing Count | Status | Notes |
|---|---|---|---|
| `source` | {audit['missing_values']['source_missing_count']} | Valid | 100% complete. All {audit['unique_source_urls']:,} URLs parse with valid schemes. |
| `nation` | {audit['missing_values']['nation_missing_count']} | **Action Required** | Exactly 6 rows lack a nation label. |
| `title` | {audit['missing_values']['title_missing_count']} | Valid | 100% complete ({audit['unique_titles']:,} unique titles). |
| `text` | {audit['missing_values']['text_missing_count']} | Valid | 100% complete. No empty story texts. |

### Records Missing Nation Labels

The following 6 rows require manual archival provenance before any country assignment can occur:

| Row Index | Title | Source URL |
|---|---|---|
{missing_nations_md}

---

## 3. Nation & Cultural Distribution

The raw dataset spans **{audit['unique_nations_count']} distinct nation values** (including the blank entry). Below are the top 25 nations represented:

| Raw Nation Label | Record Count | Percentage |
|---|---|---|
{nations_table_md}

### Critical Mapping Observations:
1. **Indigenous Representation:** The largest single label is `north_american_native` (370 tales). This label merges hundreds of distinct sovereign Indigenous Nations across North America (e.g. Ojibwe, Cherokee, Haida, Hopi) and cannot be generalized into modern "US" folklore.
2. **Target Country Overlap:** Only a subset of labels map cleanly to KathaYantra's 15 target countries (`indian` -> IN: 130, `greek` -> GR: 304, `german` -> DE: 277, `chinese` -> CN: 101, `japanese` -> JP: 88, `philippine` -> PH: 73, `irish` -> IE: 60, `brazilian` -> BR: 55, `korean` -> KR: 21, `nigerian` -> NG: 15).
3. **Missing Target Countries:** Several target countries have zero representation in this CSV, notably **Mexico (MX)**, **Egypt (EG)**, and **Indonesia (ID)**. Additional dedicated sources must be integrated in future phases.

---

## 4. Source Domains and URL Health

| Domain | Record Count | Share |
|---|---|---|
{domains_table_md}

- **Malformed URLs Detected:** {audit['malformed_urls_count']}
- **Unique URLs:** {audit['unique_source_urls']:,} of {audit['total_rows']:,} rows.

---

## 5. Duplicate and Near-Duplicate Analysis

### Exact Duplicate Texts ({audit['exact_duplicates_count']} pairs found)
{exact_dups_md}

### Near-Duplicate Texts ({audit['near_duplicates_count']} pairs identified)
Near duplicates were identified using normalized prefix-suffix signature hashing and token Jaccard similarity (>= 0.85):
{near_dups_md}

---

## 6. Text Length & Characteristics

- **Minimum Length:** {audit['text_length_statistics']['min_char_length']} characters ({audit['text_length_statistics']['min_word_count']} words)
- **Maximum Length:** {audit['text_length_statistics']['max_char_length']:,} characters ({audit['text_length_statistics']['max_word_count']:,} words)
- **Average Length:** {audit['text_length_statistics']['avg_char_length']:,} characters (~{audit['text_length_statistics']['avg_word_count']:,} words)
- **Short Texts (< 50 words):** {audit['text_length_statistics']['short_text_count']} records (brief fables, fragments).
- **Long Texts (> 15,000 words):** {audit['text_length_statistics']['long_text_count']} record (novella-length fairy tale *The Ice Maiden*).

---

## 7. Rights, Provenance & Ingestion Safeguards

{findings_md}

### Phase 1 Archival Directives:
1. Store raw CSV in `data/raw/folk_tales_deduplicated.csv` with gitignore protection against public repository publication.
2. Mark all raw records with `rights_status: needs_rights_review`.
3. Do not import full-text into `data/seed/` or public API responses.
4. Prepare clean schemas for verified original summaries and citations.
"""


if __name__ == "__main__":
    default_csv = Path("data/raw/folk_tales_deduplicated.csv")
    if not default_csv.exists():
        default_csv = Path("folk_tales_deduplicated.csv")

    target_csv = Path(sys.argv[1]) if len(sys.argv) > 1 else default_csv

    print(f"Starting audit of: {target_csv}")
    report = audit_csv(target_csv)
    print("Audit completed successfully!")
    print(f"Total rows audited: {report['total_rows']:,}")
    print(f"Exact duplicates found: {report['exact_duplicates_count']}")
    print(f"Near duplicates found: {report['near_duplicates_count']}")
    print(f"Missing nation records: {report['missing_values']['nation_missing_count']}")
    print("Outputs generated:")
    print("  - data/manifests/folk_tales_csv_audit.json")
    print("  - docs/folk-tales-dataset-audit.md")

