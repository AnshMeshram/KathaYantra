"""Tests for JSON Schema Draft 2020-12 Exports and Contract Verification (Phase 2)."""

import json
from pathlib import Path
import pytest
from scripts.export_json_schemas import (
    DRAFT_2020_12_URI,
    MODELS_TO_EXPORT,
    export_all_schemas,
)

REQUIRED_SCHEMA_FILES = [
    "country.schema.json",
    "story.schema.json",
    "source.schema.json",
    "source_registry_item.schema.json",
    "import_candidate.schema.json",
    "generated_fiction.schema.json",
    "dataset_envelope.schema.json",
    "dataset_manifest.schema.json",
]


def test_all_required_json_schemas_exist_and_are_valid():
    """Verify that all 8 required JSON Schema files exist and parse as valid JSON."""
    schemas_dir = Path("data/schemas")
    assert schemas_dir.exists(), "data/schemas directory must exist"

    for filename in REQUIRED_SCHEMA_FILES:
        schema_path = schemas_dir / filename
        assert schema_path.exists(), f"Schema file {filename} is missing"

        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "$schema" in data
        assert data["$schema"] == DRAFT_2020_12_URI
        assert "type" in data or "properties" in data or "$defs" in data


def test_schema_export_reproducibility(tmp_path: Path):
    """Verify that exporting schemas into a temporary path produces identical output."""
    paths = export_all_schemas(output_dir=tmp_path)
    assert len(paths) == 8

    schemas_dir = Path("data/schemas")
    for filename in REQUIRED_SCHEMA_FILES:
        expected_content = (schemas_dir / filename).read_text(encoding="utf-8")
        actual_content = (tmp_path / filename).read_text(encoding="utf-8")
        assert actual_content == expected_content, f"Schema {filename} differs from exported output"

