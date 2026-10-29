"""Tests for the Central KathaYantra Import Pipeline."""

from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.integrations.registry import SourceRegistryManager
from app.repositories.candidate_repository import CandidateRepository
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum
from app.services.import_batch_service import ImportBatchService
from app.services.import_pipeline import ImportPipeline


@pytest.fixture
def mock_pipeline_setup(tmp_path: Path):
    repo = CandidateRepository(storage_dir=tmp_path / "candidates")
    batch_srv = ImportBatchService(repository=repo)
    reg_mgr = MagicMock(spec=SourceRegistryManager)

    pipeline = ImportPipeline(
        registry_manager=reg_mgr,
        batch_service=batch_srv,
        repository=repo,
    )
    return pipeline, reg_mgr, repo


@pytest.mark.asyncio
async def test_pipeline_dry_run_does_not_persist(mock_pipeline_setup):
    pipeline, reg_mgr, repo = mock_pipeline_setup

    mock_connector = AsyncMock()
    mock_connector.search.return_value = [
        ImportCandidate(
            candidate_id="CAND-DRY-001",
            import_batch_id="batch-dry",
            raw_title="Dry Run Story",
            raw_url="https://example.com/dry",
            proposed_country_code="IN",
            proposed_category=CategoryEnum.FOLKLORE,
            rights_status=RightsStatusEnum.APPROVED,
        )
    ]
    reg_mgr.get_connector.return_value = mock_connector

    manifest = await pipeline.run_import_batch(
        source_id="test_src",
        query="test query",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        dry_run=True,
    )

    assert manifest.dry_run is True
    assert manifest.retrieved_count == 1
    # Check that repository wrote nothing
    assert len(repo.load_all_candidates()) == 0


@pytest.mark.asyncio
async def test_pipeline_persistence_and_disposition(mock_pipeline_setup):
    pipeline, reg_mgr, repo = mock_pipeline_setup

    mock_connector = AsyncMock()
    mock_connector.search.return_value = [
        # Candidate 1: Cleared rights and supported country -> ELIGIBLE_FOR_EDITORIAL_REVIEW
        ImportCandidate(
            candidate_id="CAND-STG-001",
            import_batch_id="batch-stg",
            raw_title="Panchatantra Tale",
            raw_url="https://example.com/panchatantra",
            proposed_country_code="IN",
            proposed_category=CategoryEnum.FOLKLORE,
            rights_status=RightsStatusEnum.APPROVED,
        ),
        # Candidate 2: Unknown rights -> NEEDS_RIGHTS_REVIEW
        ImportCandidate(
            candidate_id="CAND-STG-002",
            import_batch_id="batch-stg",
            raw_title="Unchecked Lore",
            raw_url="https://example.com/lore",
            proposed_country_code="JP",
            proposed_category=CategoryEnum.FOLKLORE,
            rights_status=RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
        ),
    ]
    reg_mgr.get_connector.return_value = mock_connector

    manifest = await pipeline.run_import_batch(
        source_id="test_src",
        query="folklore",
        country_code="IN",
        category=CategoryEnum.FOLKLORE,
        dry_run=False,
    )

    assert manifest.dry_run is False
    assert manifest.retrieved_count == 2
    assert manifest.rights_pending_count == 1

    staged = repo.load_batch(manifest.batch_id)
    assert len(staged) == 2
    assert staged[0].disposition == CandidateDispositionEnum.ELIGIBLE_FOR_EDITORIAL_REVIEW
    assert staged[1].disposition == CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW
