"""Tests for ImportCandidate Schema and Staging Lifecycle (Phase 2)."""

from pydantic import ValidationError
import pytest
from app.schemas.import_candidate import (
    CandidateDispositionEnum,
    ImportCandidate,
)
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum, StoryRecord, VerificationStatusEnum


def test_valid_incomplete_import_candidate():
    """Verify that an incomplete raw source record can be staged as an ImportCandidate.

    This ensures that raw, uncertain upstream data does not weaken published StoryRecord requirements.
    """
    candidate = ImportCandidate(
        candidate_id="CAND-FT-001289",
        import_batch_id="batch_fairytalez_20261029",
        source_registry_id="fairytalez_raw",
        raw_title="The Seven Stages of Roostem",
        raw_nation="",  # Missing nation in raw CSV row 1289!
        raw_url="https://fairytalez.com/seven-stages-roostem/",
        raw_metadata={"row_index": 1289, "original_source": "fairytalez.com"},
        raw_text_available=True,
        disposition=CandidateDispositionEnum.NEEDS_MAPPING_REVIEW,
    )

    assert candidate.candidate_id == "CAND-FT-001289"
    assert candidate.raw_nation == ""
    assert candidate.proposed_country_code is None
    assert candidate.disposition == CandidateDispositionEnum.NEEDS_MAPPING_REVIEW
    assert candidate.rights_status == RightsStatusEnum.NEEDS_RIGHTS_REVIEW


def test_candidate_and_published_story_record_remain_distinct():
    """Verify that an ImportCandidate cannot masquerade as a published StoryRecord."""
    candidate = ImportCandidate(
        candidate_id="CAND-2026-0001",
        import_batch_id="batch_001",
        raw_title="Raw Tale Without Summary",
    )

    # An ImportCandidate is not a StoryRecord
    assert not isinstance(candidate, StoryRecord)

    # Attempting to validate incomplete candidate data as StoryRecord must fail
    with pytest.raises(ValidationError):
        StoryRecord(
            id=candidate.candidate_id,  # Invalid format
            title=candidate.raw_title,
            country_code="IN",
            category=CategoryEnum.FOLKLORE,
            summary="",  # Incomplete / missing summary fails
            sources=[],  # Missing sources fails
        )


def test_candidate_disposition_transitions():
    """Verify valid candidate lifecycle dispositions."""
    candidate = ImportCandidate(
        candidate_id="CAND-2026-0002",
        import_batch_id="batch_001",
        raw_title="Staged Candidate",
        disposition=CandidateDispositionEnum.NEW_CANDIDATE,
    )

    # Transition to rights review
    candidate.disposition = CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW
    assert candidate.disposition == CandidateDispositionEnum.NEEDS_RIGHTS_REVIEW

    # Transition to rejected
    candidate.disposition = CandidateDispositionEnum.REJECTED
    assert candidate.disposition == CandidateDispositionEnum.REJECTED

