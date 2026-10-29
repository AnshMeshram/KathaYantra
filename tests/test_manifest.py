"""Tests for KathaYantra Dataset Manifest Generation and Integrity Checking."""

import json
from pathlib import Path
import pytest
from app.core.config import settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.services.manifest_service import ManifestService, manifest_service


def test_manifest_calculation_from_actual_data():
    """Test 15: Manifest calculation accurately reads actual files and avoids false claims."""
    manifest = manifest_service.compute_manifest()

    # Quota verification
    assert manifest.required_record_count == 300
    
    assert manifest.target_breakdown.total_countries == 15
    assert manifest.target_breakdown.per_country_folklore == 10
    assert manifest.target_breakdown.per_country_urban_legends == 10

    # True actual counts (verified records populated in Phase 4)
    assert manifest.current_actual_counts.total_records == 300
    assert manifest.current_actual_counts.folklore_records == 150
    assert manifest.current_actual_counts.urban_legend_records == 150

    # Country list matches the 15 supported countries
    assert len(manifest.country_list) == 15
    assert set(manifest.country_list) == set(SUPPORTED_COUNTRY_CODES.keys())

    # All 15 countries have explicit counts in both categories
    for c in manifest.country_list:
        assert c in manifest.folklore_counts_by_country
        assert c in manifest.urban_legend_counts_by_country


def test_manifest_dynamic_calculation_with_fixture(tmp_path: Path):
    """Verify that ManifestService correctly counts records when files contain data."""
    folk_dir = tmp_path / "folklore"
    urban_dir = tmp_path / "urban_legends"
    folk_dir.mkdir()
    urban_dir.mkdir()

    # Populate a test fixture for IN folklore with 2 records
    in_folk_data = {
        "country_code": "IN",
        "category": "folklore",
        "records": [
            {
                "id": "IN-FOLK-001",
                "title": "Tale 1",
                "verification_status": "verified",
                "rights_status": "approved",
                "sources": [{"name": "Source A", "url": "https://example.com/a"}],
            },
            {
                "id": "IN-FOLK-002",
                "title": "Tale 2",
                "verification_status": "needs_review",
                "rights_status": "needs_rights_review",
                "sources": [{"name": "Source B", "url": "https://example.com/b"}],
            },
        ],
    }
    with open(folk_dir / "IN.json", "w", encoding="utf-8") as f:
        json.dump(in_folk_data, f)

    # Populate a test fixture for US urban legends with 1 record
    us_urban_data = {
        "country_code": "US",
        "category": "urban_legend",
        "records": [
            {
                "id": "US-URBAN-001",
                "title": "Mothman",
                "verification_status": "verified",
                "rights_status": "approved",
                "sources": [{"name": "Source C", "url": "https://example.com/c"}],
            }
        ],
    }
    with open(urban_dir / "US.json", "w", encoding="utf-8") as f:
        json.dump(us_urban_data, f)

    test_service = ManifestService(
        folklore_dir=folk_dir,
        urban_dir=urban_dir,
        manifest_file=tmp_path / "manifest.json",
    )

    manifest = test_service.compute_manifest()

    assert manifest.current_actual_counts.total_records == 3
    assert manifest.current_actual_counts.folklore_records == 2
    assert manifest.current_actual_counts.urban_legend_records == 1
    assert manifest.folklore_counts_by_country["IN"] == 2
    assert manifest.urban_legend_counts_by_country["US"] == 1
    assert manifest.unverified_records == 1
    assert manifest.rights_pending_records == 1
    assert "Source A" in manifest.source_coverage
    assert "Source C" in manifest.source_coverage
