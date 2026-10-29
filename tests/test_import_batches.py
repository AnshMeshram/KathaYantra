"""Tests for Import Batch Manifest Tracking and Coverage Reporting."""

from pathlib import Path
import pytest
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.story import CategoryEnum
from app.services.import_batch_service import ImportBatchService
from app.services.import_reporting import ImportReportingService


@pytest.fixture
def temp_repo(tmp_path: Path):
    return CandidateRepository(storage_dir=tmp_path / "candidates")


def test_batch_save_and_load(temp_repo):
    cands = [
        ImportCandidate(
            candidate_id="CAND-TEST-001",
            import_batch_id="batch-test-1",
            raw_title="Kitsune Tale",
            proposed_country_code="JP",
            proposed_category=CategoryEnum.FOLKLORE,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
        ),
        ImportCandidate(
            candidate_id="CAND-TEST-002",
            import_batch_id="batch-test-1",
            raw_title="Teke Teke Legend",
            proposed_country_code="JP",
            proposed_category=CategoryEnum.URBAN_LEGEND,
            disposition=CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW,
        ),
    ]

    batch_service = ImportBatchService(repository=temp_repo)
    manifest = batch_service.compile_manifest(
        batch_id="batch-test-1",
        source_id="wikimedia_wikipedia_api",
        query="Japanese folklore",
        candidates=cands,
        start_time=1000.0,
        country_code="JP",
    )

    saved_path = batch_service.persist_batch("batch-test-1", cands, manifest)
    assert saved_path is not None
    assert Path(saved_path).exists()

    loaded = temp_repo.load_batch("batch-test-1")
    assert len(loaded) == 2
    assert loaded[0].candidate_id == "CAND-TEST-001"
    assert loaded[1].candidate_id == "CAND-TEST-002"

    meta = temp_repo.get_batch_metadata("batch-test-1")
    assert meta is not None
    assert meta["batch_id"] == "batch-test-1"
    assert meta["retrieved_count"] == 2
    assert meta["accepted_count"] == 1
    assert meta["rights_pending_count"] == 1


def test_reporting_service_formats_output(temp_repo):
    # Save a test batch in temp_repo
    cands = [
        ImportCandidate(
            candidate_id="CAND-TEST-IN-001",
            import_batch_id="batch-in",
            raw_title="Baital Pachisi",
            proposed_country_code="IN",
            proposed_category=CategoryEnum.FOLKLORE,
            disposition=CandidateDispositionEnum.ELIGIBLE_FOR_EDITORIAL_REVIEW,
        )
    ]
    batch_service = ImportBatchService(repository=temp_repo)
    manifest = batch_service.compile_manifest(
        batch_id="batch-in",
        source_id="wikimedia",
        query="Baital",
        candidates=cands,
        start_time=1000.0,
    )
    batch_service.persist_batch("batch-in", cands, manifest)

    reporting = ImportReportingService(repository=temp_repo)
    report_dict = reporting.generate_coverage_report()

    assert report_dict["summary"]["total_staged_candidates"] == 1
    assert report_dict["summary"]["required_catalogue_target"] == 300
    assert report_dict["country_matrix"]["IN"]["staged_candidate_folklore"] == 1

    text_report = reporting.format_text_report()
    assert "KATHAYANTRA — INGESTION PIPELINE & CANDIDATE COVERAGE REPORT" in text_report
    assert "IN" in text_report
