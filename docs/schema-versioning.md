# KathaYantra Schema Versioning and Migration Policy

> **Core Archival Principle:**  
> *Preserve the story. Trace the source. Respect the culture. Keep the AI honest.*

---

## 1. Versioning Philosophy

KathaYantra treats its data structures as formal, version-controlled **contracts**. All data ingested, archived, exported, or served across the REST API adheres to explicit semantic versioning (`MAJOR.MINOR.PATCH`).

### Schema Contract Versions (Current: `2.0.0`)

| Schema Contract | Model Class | JSON Schema File | Current Version | Status |
|---|---|---|---|---|
| **Country Registry** | `CountryRecord` | `country.schema.json` | `2.0.0` | Active Canonical |
| **Story Record** | `StoryRecord` | `story.schema.json` | `2.0.0` | Active Canonical |
| **Source Citation** | `StorySource` | `source.schema.json` | `2.0.0` | Active Canonical |
| **Source Registry** | `SourceRegistryItem` | `source_registry_item.schema.json` | `2.0.0` | Active Canonical |
| **Import Candidate** | `ImportCandidate` | `import_candidate.schema.json` | `2.0.0` | Active Canonical |
| **AI Creative Fiction** | `GeneratedFictionRecord` | `generated_fiction.schema.json` | `2.0.0` | Active Canonical |
| **Dataset Envelope** | `DatasetEnvelope` | `dataset_envelope.schema.json` | `2.0.0` | Active Canonical |
| **Dataset Manifest** | `DatasetManifest` | `dataset_manifest.schema.json` | `2.0.0` | Active Canonical |

---

## 2. Backward Compatibility & Breaking Changes

### Backward-Compatible Changes (Minor / Patch increments)
- Adding optional fields with safe defaults (`Field(default=None)` or `Field(default_factory=list)`).
- Adding new enum values to extensible registries (e.g. new `source_type`).
- Adding read-only properties or helper aliases (e.g. `CountryRecord.region`, `StorySource.name`).
- Enhancing documentation or descriptions in Pydantic models.

### Breaking Changes (Major increments)
- Renaming or removing existing required fields.
- Changing field data types or tightening validation constraints in a way that invalidates existing records.
- Altering the shape of the dataset envelope (e.g. Phase 1 simple structure to Phase 2 `DatasetEnvelope`).
- Changing the primary identifier convention (`^[A-Z]{2}-(FOLK|URBAN)-[0-9]{3,}$`).

---

## 3. The Dataset Envelope Migration Pipeline

In Phase 1, country seed files used a preliminary envelope structure:
```json
{
  "country_code": "IN",
  "category": "folklore",
  "records": [],
  "metadata": {
    "total_records": 0,
    "target_count": 10,
    "status": "pending_curation",
    "last_updated": "2026-10-29T12:00:00Z"
  }
}
```

In Phase 2, all 30 files are standardized on the canonical `DatasetEnvelope` (`schema_version: "2.0.0"`):
```json
{
  "schema_version": "2.0.0",
  "dataset_id": "IN-folklore",
  "country_code": "IN",
  "category": "folklore",
  "records": [],
  "metadata": {
    "description": "Folklore archive partition for India (IN)",
    "dataset_version": "2.0.0",
    "created_at": "2026-10-29T12:00:00Z",
    "updated_at": "2026-10-29T12:00:00Z",
    "provenance_notes": "Canonical Phase 2 DatasetEnvelope schema format",
    "target_count": 10,
    "actual_record_count": 0,
    "total_records": 0,
    "status": "pending_curation",
    "validation_status": "valid",
    "last_updated": "2026-10-29T12:00:00Z",
    "import_batch_references": []
  }
}
```

### Migration Safeguards
The migration script [`scripts/migrate_seed_json.py`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/scripts/migrate_seed_json.py) guarantees:
1. **Zero Record Loss:** Any pre-existing curated story records are preserved without alteration.
2. **Idempotence:** Running the migration script multiple times produces zero changes once files conform to `2.0.0`.
3. **Non-Destructive `--check` Mode:** Validates conformance without touching filesystem assets. Returns exit code `0` if all files conform, `1` if migration is needed.

```bash
# Non-destructive conformance check
python scripts/migrate_seed_json.py --check

# Execute idempotent migration
python scripts/migrate_seed_json.py
```

---

## 4. Exporting JSON Schema Draft 2020-12 Specifications

KathaYantra generates authoritative JSON Schema Draft 2020-12 documents directly from its Pydantic v2 models. Hand-edited schemas are strictly prohibited to prevent schema drift.

```bash
python scripts/export_json_schemas.py
```

Outputs are written deterministically to:
- [`data/schemas/country.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/country.schema.json)
- [`data/schemas/story.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/story.schema.json)
- [`data/schemas/source.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/source.schema.json)
- [`data/schemas/source_registry_item.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/source_registry_item.schema.json)
- [`data/schemas/import_candidate.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/import_candidate.schema.json)
- [`data/schemas/generated_fiction.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/generated_fiction.schema.json)
- [`data/schemas/dataset_envelope.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/dataset_envelope.schema.json)
- [`data/schemas/dataset_manifest.schema.json`](file:///C:/Users/shrin/Desktop/Hactoberfest2026/KathaYantra/data/schemas/dataset_manifest.schema.json)

---

## 5. Automated Data Quality & Archival Validation

The data quality engine validates all 30 seed files against 17 discrete archival checks:

```bash
python scripts/validate_json_datasets.py
```

- Returns exit code `0` if all checks pass.
- Returns exit code `1` if fatal schema or provenance errors are detected.
- Emits structured warnings for curatorial review (e.g. recurring titles across countries).
