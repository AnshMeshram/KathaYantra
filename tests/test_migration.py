"""Tests for Seed JSON Migration Utility (Phase 2)."""

import json
from pathlib import Path
import pytest
from app.schemas.story import CategoryEnum
from scripts.migrate_seed_json import (
    inspect_file_needs_migration,
    migrate_seed_file,
    process_all_seed_files,
)


def test_migration_check_on_current_workspace_returns_zero():
    """Verify that process_all_seed_files(check_only=True) returns 0 on current workspace."""
    exit_code = process_all_seed_files(check_only=True)
    assert exit_code == 0


def test_migration_upgrades_legacy_fixture_without_losing_records(tmp_path: Path):
    """Verify that a legacy Phase 1 fixture is upgraded to 2.0.0 preserving its records."""
    legacy_file = tmp_path / "IN.json"
    legacy_data = {
        "country_code": "IN",
        "category": "folklore",
        "records": [
            {
                "id": "IN-FOLK-001",
                "title": "Legacy Preserved Tale",
                "country_code": "IN",
                "category": "folklore",
                "summary": "This is a preserved tale from Phase 1 curation.",
                "sources": [{"title": "Old Source", "url": "https://example.com/old"}],
            }
        ],
        "metadata": {
            "total_records": 1,
            "status": "in_review",
        },
    }
    with open(legacy_file, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f)

    assert inspect_file_needs_migration(legacy_file, "IN", CategoryEnum.FOLKLORE) is True

    envelope = migrate_seed_file(legacy_file, "IN", CategoryEnum.FOLKLORE)

    assert envelope.schema_version == "2.0.0"
    assert envelope.dataset_id == "IN-folklore"
    assert len(envelope.records) == 1
    assert envelope.records[0].title == "Legacy Preserved Tale"
    assert envelope.metadata.actual_record_count == 1
    assert envelope.metadata.status == "in_review"

    # Running check again shows it is up to date
    assert inspect_file_needs_migration(legacy_file, "IN", CategoryEnum.FOLKLORE) is False
