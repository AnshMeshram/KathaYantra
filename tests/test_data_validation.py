"""Tests for Data Quality Validator and Governance Engine (Phase 2)."""

import json
from pathlib import Path
import pytest
from app.services.data_validation import (
    DataQualityValidator,
    DataValidationReport,
    data_quality_validator,
)


def test_validator_passes_on_current_canonical_seed_files():
    """Verify that data_quality_validator passes with 0 errors across all 30 current seed files."""
    report = data_quality_validator.validate_all()
    assert report.is_valid is True
    assert report.total_files_inspected == 30
    assert report.error_count == 0
    assert len(report.counts_by_country) == 15


def test_validator_detects_corrupted_json(tmp_path: Path):
    """Verify that corrupt JSON in a seed file produces a fatal validation error."""
    folk_dir = tmp_path / "folklore"
    urban_dir = tmp_path / "urban_legends"
    folk_dir.mkdir()
    urban_dir.mkdir()

    # Corrupt JSON file for IN
    bad_file = folk_dir / "IN.json"
    bad_file.write_text("{ unclosed json: ", encoding="utf-8")

    validator = DataQualityValidator(folklore_dir=folk_dir, urban_dir=urban_dir)
    report = validator.validate_all()

    assert report.is_valid is False
    assert any(i.error_code == "JSON_SYNTAX_ERROR" for i in report.issues)


def test_validator_detects_duplicate_id_across_different_files(tmp_path: Path):
    """Verify detection of duplicate record IDs across different country/category files."""
    folk_dir = tmp_path / "folklore"
    urban_dir = tmp_path / "urban_legends"
    folk_dir.mkdir()
    urban_dir.mkdir()

    # File 1: IN folklore
    in_envelope = {
        "schema_version": "2.0.0",
        "dataset_id": "IN-folklore",
        "country_code": "IN",
        "category": "folklore",
        "records": [
            {
                "id": "IN-FOLK-001",
                "title": "Tale In",
                "country_code": "IN",
                "category": "folklore",
                "summary": "Valid summary description for testing.",
                "sources": [{"title": "Src", "url": "https://example.com/a"}],
            }
        ],
    }
    with open(folk_dir / "IN.json", "w", encoding="utf-8") as f:
        json.dump(in_envelope, f)

    # File 2: JP folklore maliciously reusing IN-FOLK-001 (or corrupted prefix)
    jp_envelope = {
        "schema_version": "2.0.0",
        "dataset_id": "JP-folklore",
        "country_code": "JP",
        "category": "folklore",
        "records": [
            {
                "id": "IN-FOLK-001",  # Duplicate ID
                "title": "Tale Jp",
                "country_code": "JP",
                "category": "folklore",
                "summary": "Valid summary description for testing.",
                "sources": [{"title": "Src", "url": "https://example.com/b"}],
            }
        ],
    }
    with open(folk_dir / "JP.json", "w", encoding="utf-8") as f:
        json.dump(jp_envelope, f)

    validator = DataQualityValidator(folklore_dir=folk_dir, urban_dir=urban_dir)
    report = validator.validate_all()

    assert report.is_valid is False
    assert any(i.error_code == "DUPLICATE_RECORD_ID" for i in report.issues)
