# KathaYantra — Deterministic Retrieval Architecture Specification
### *SQLite FTS5 Lexical Search, BM25 Ranking, and Archival Gating*

---

## 1. Design Rationale

While modern AI projects frequently reach for complex external vector databases and cloud embeddings, **KathaYantra** prioritizes:
1. **Zero External Cloud Dependencies:** Everything runs 100% offline.
2. **Determinism & Reproducibility:** The exact same query against the same dataset must yield the exact same ranked evidence.
3. **Low Hardware Overhead:** Runs effortlessly on standard laptops and developer workstations without requiring 16GB of dedicated VRAM.
4. **Exact Linguistic & Name Matching:** Traditional cultural entities (*Yōkai*, *Afrit*, *Dokkaebi*, *Saci-Pererê*, *Betal*) require precise lexical and token-prefix matching rather than fuzzy semantic approximations that conflate distinct regional figures.

To achieve this, KathaYantra implements **SQLite FTS5 (Full-Text Search 5)** as the core retrieval engine.

---

## 2. Index Structure & Field Weighting

The search index is stored in an atomic SQLite database at `data/processed/retrieval/retrieval_index.db`.

### FTS5 Virtual Table Schema:
```sql
CREATE VIRTUAL TABLE stories_fts USING fts5(
    id UNINDEXED,
    country_code UNINDEXED,
    category UNINDEXED,
    title,
    alternate_names,
    summary,
    motifs,
    themes,
    cultural_community,
    region,
    sources_json UNINDEXED,
    attribution_text UNINDEXED,
    verification_status UNINDEXED,
    rights_status UNINDEXED,
    dataset_path UNINDEXED,
    tokenize = 'unicode61'
);
```

### BM25 Field Weighting:
When calculating ranking scores, fields are weighted according to their curatorial significance:

```sql
SELECT id, ..., bm25(stories_fts, 5.0, 2.0, 1.0, 1.5, 1.0, 2.0, 1.0) AS bm25_rank
FROM stories_fts
WHERE stories_fts MATCH :query
ORDER BY bm25_rank ASC
LIMIT :limit;
```

- `title` **(5.0x):** Matches in canonical narrative titles receive the highest relevance boost.
- `cultural_community` & `alternate_names` **(2.0x):** Regional and community terms (e.g. *Nahua*, *Yoruba*, *Gaelic*) receive high priority.
- `motifs` **(1.5x):** Thompson motif index tags (e.g. `E411`, `G510`) prioritize thematic alignment.
- `summary`, `themes`, `region` **(1.0x):** Narrative synopses provide baseline descriptive evidence.

---

## 3. Publication Policy & Integrity Gating

The retrieval index is strictly derived from the approved `data/seed/` dataset envelopes through `retrieval_index_service.rebuild_index()`.

Every candidate record undergoes a strict 5-stage filter before entering the index:
1. **Duplicate ID Check:** Prevents collisions and duplicate listings.
2. **Anti-Fiction Check:** `ContentOriginEnum.AI_GENERATED_FICTION` records are permanently barred from the authentic folklore search index.
3. **Verification Check:** `verification_status` must equal `VerificationStatusEnum.VERIFIED`.
4. **Rights Check:** `rights_status` must be `approved` or `public_domain_verified`.
5. **Deterministic Policy Gate:** All 10 rules of `PublicationPolicy.evaluate_eligibility(story)` must pass.

---

## 4. Query Sanitization & Stopword Elimination

User inquiries often contain conversational phrasing (*"Tell me about the..."*, *"What is a..."*). If tokenized naively, frequent English stopwords would match nearly all documents in the corpus.

The `RetrievalService` applies deterministic sanitization:
1. **Punctuation Stripping:** Cleans quotes, question marks, exclamation points, and parentheses that could corrupt FTS5 syntax.
2. **Stopword Filtering:** Eliminates 60+ common conversational stopwords (`the`, `a`, `about`, `tell`, `me`, `who`, `what`, `where`, `is`, `of`).
3. **Prefix Wildcards:** Extends tokens with `*` (e.g. `"mothman"* OR "banshee"*`) to match morphological inflections.

---

## 5. Index Management CLI Tools

### Rebuild Retrieval Index:
```bash
# Live compile & persist to SQLite
python scripts/build_retrieval_index.py

# Dry-run audit without disk writes
python scripts/build_retrieval_index.py --dry-run
```

### Inspect Index Health & Breakdown:
```bash
python scripts/audit_retrieval_index.py
```
*Outputs indexed story counts broken down by category and country.*

---

## 6. Future Semantic Embedding Blueprint

The retrieval architecture is engineered to accommodate local vector embeddings in future iterations without replacing lexical search:

```
[ User Query ]
       │
       ├───> [ SQLite FTS5 Lexical Match ] ───┐
       │                                       ├──> [ Reciprocal Rank Fusion (RRF) ] ──> Top Records
       └───> [ Optional Local Embedding ] ────┘
             (e.g. nomic-embed-text via Ollama)
```

1. **Non-Breaking Extension:** Lexical search remains the default and always functions even if no embedding model is installed.
2. **Local Model Only:** Any future embedding runner must use locally hosted models via Ollama (e.g. `nomic-embed-text`), never third-party cloud vector services.
3. **Hybrid RRF Ranking:** Lexical BM25 and vector cosine similarity are blended via Reciprocal Rank Fusion to ensure exact name matches never get buried.
