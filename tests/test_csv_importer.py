"""Tests for the Quarantined Raw Folktales CSV Candidate Importer."""

import csv
from pathlib import Path
import pytest
from app.integrations.csv_importer import CSVFolktalesImporter
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum


@pytest.fixture
def sample_csv_fixture(tmp_path: Path):
    csv_file = tmp_path / "sample_folktales.csv"
    rows = [
        ["source", "nation", "title", "text"],
        ["https://fairytalez.com/the-saci/", "brazilian", "The Legend of the Saci", "Long story text about Saci Perere..."],
        ["https://fairytalez.com/coyote-tales/", "north_american_native", "Coyote and the Monster", "Coyote trickster oral lore..."],
        ["https://fairytalez.com/missing-nation-tale/", "", "Mysterious Nameless Folktale", "Unknown origin tale..."],
        ["https://fairytalez.com/the-saci/", "brazilian", "The Legend of the Saci", "Identical duplicate row..."],
    ]
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return csv_file


@pytest.mark.asyncio
async def test_csv_importer_maps_clean_nation_to_rights_review(sample_csv_fixture):
    importer = CSVFolktalesImporter(csv_path=sample_csv_fixture)
    candidates = await importer.search(limit=10)

    assert len(candidates) == 4

    # Row 1: Brazilian -> BR, needs rights review
    cand1 = candidates[0]
    assert isinstance(cand1, ImportCandidate)
    assert cand1.raw_title == "The Legend of the Saci"
    assert cand1.proposed_country_code == "BR"
    assert cand1.disposition == CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW
    assert cand1.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW
    # Text length recorded in metadata, but raw story text not exposed in candidate summary
    assert cand1.raw_metadata["text_length"] > 0
    assert "Long story text" not in (cand1.proposed_summary or "")


@pytest.mark.asyncio
async def test_csv_importer_routes_ambiguous_or_missing_nation(sample_csv_fixture):
    importer = CSVFolktalesImporter(csv_path=sample_csv_fixture)
    candidates = await importer.search(limit=10)

    # Row 2: north_american_native -> needs mapping review (indigenous sovereignty requirement)
    cand2 = candidates[1]
    assert cand2.raw_nation == "north_american_native"
    assert cand2.disposition == CandidateDispositionEnum.NEEDS_MAPPING_REVIEW

    # Row 3: Missing nation -> needs mapping review
    cand3 = candidates[2]
    assert cand3.raw_nation == ""
    assert cand3.disposition == CandidateDispositionEnum.NEEDS_MAPPING_REVIEW


@pytest.mark.asyncio
async def test_csv_importer_detects_duplicates(sample_csv_fixture):
    importer = CSVFolktalesImporter(csv_path=sample_csv_fixture)
    candidates = await importer.search(limit=10)

    # Row 4: Duplicate of row 1
    cand4 = candidates[3]
    assert cand4.disposition == CandidateDispositionEnum.DUPLICATE_CANDIDATE
