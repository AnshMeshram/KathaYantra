"""Tests for Candidate Deduplication and Cultural Variant Analysis."""

import pytest
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.services.candidate_deduplication import CandidateDeduplicator


def test_exact_duplicate_detection():
    cand1 = ImportCandidate(
        candidate_id="CAND-001",
        import_batch_id="batch-1",
        source_registry_id="test_source",
        external_id="ext-1",
        raw_title="The Flying Dutchman",
        raw_url="https://example.com/dutchman",
    )
    cand2 = ImportCandidate(
        candidate_id="CAND-002",
        import_batch_id="batch-1",
        source_registry_id="test_source",
        external_id="ext-1",
        raw_title="The Flying Dutchman",
        raw_url="https://example.com/dutchman",
    )

    seen = set()
    res1 = CandidateDeduplicator.process_candidate(cand1, seen)
    assert res1.disposition != CandidateDispositionEnum.DUPLICATE_CANDIDATE

    res2 = CandidateDeduplicator.process_candidate(cand2, seen)
    assert res2.disposition == CandidateDispositionEnum.DUPLICATE_CANDIDATE
    assert "Exact duplicate detected" in (res2.review_notes or "")


def test_cultural_variant_similarity_does_not_merge():
    """Prove that similar titles from different cultural traditions are NOT merged."""
    existing_irish = ImportCandidate(
        candidate_id="CAND-IE-001",
        import_batch_id="batch-1",
        source_registry_id="myths_of_ireland",
        external_id="moi-1",
        raw_title="The Story of the Weeping Woman of the Lake",
        raw_url="https://example.com/irish-lake",
        proposed_country_code="IE",
    )
    new_mexican = ImportCandidate(
        candidate_id="CAND-MX-001",
        import_batch_id="batch-2",
        source_registry_id="mexican_archive",
        external_id="mx-1",
        raw_title="The Story of the Weeping Woman La Llorona",
        raw_url="https://example.com/la-llorona",
        proposed_country_code="MX",
    )

    seen = set()
    res = CandidateDeduplicator.process_candidate(
        new_mexican,
        seen_fingerprints=seen,
        known_candidates=[existing_irish],
    )

    # Must NOT be marked duplicate!
    assert res.disposition != CandidateDispositionEnum.DUPLICATE_CANDIDATE
    # Must retain separate candidate identity
    assert res.candidate_id == "CAND-MX-001"
    # Should flag a variant review notice in notes to help human curators compare
    assert "Variant Notice" in (res.review_notes or "")
    assert "Keep separate to preserve regional traditions" in (res.review_notes or "")
