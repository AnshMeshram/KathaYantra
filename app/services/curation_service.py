"""Curation Service for KathaYantra Editorial Review and Story Record Promotion.

Bridges the staged ImportCandidate pipeline with the canonical published StoryRecord archive,
enforcing editorial review standards, copyright clearances, and publication policies.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from app.repositories.candidate_repository import CandidateRepository, candidate_repository
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)
from app.services.publication_policy import PublicationEligibilityResult, PublicationPolicy, publication_policy
from app.services.source_verification import SourceVerificationResult, SourceVerificationService, source_verification_service
from app.services.summary_builder import SummaryBuilder, summary_builder


class CurationService:
    """Orchestrates candidate review, provenance evaluation, and story record promotion."""

    def __init__(
        self,
        repository: Optional[CandidateRepository] = None,
        verification_service: Optional[SourceVerificationService] = None,
        policy: Optional[PublicationPolicy] = None,
        builder: Optional[SummaryBuilder] = None,
    ):
        self.repository = repository or candidate_repository
        self.verification_service = verification_service or source_verification_service
        self.policy = policy or publication_policy
        self.builder = builder or summary_builder

    def get_review_queue(
        self,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        disposition: Optional[CandidateDispositionEnum] = None,
    ) -> list[ImportCandidate]:
        """Fetch candidates requiring human or automated editorial review."""
        if disposition:
            return self.repository.query(
                country_code=country_code,
                category=category,
                disposition=disposition,
            )
        # Default queue: all un-finalized dispositions
        all_candidates = self.repository.load_all_candidates()
        reviewable = [
            c for c in all_candidates
            if c.disposition not in (
                CandidateDispositionEnum.APPROVED_FOR_PUBLICATION,
                CandidateDispositionEnum.REJECTED,
                CandidateDispositionEnum.DUPLICATE_CANDIDATE,
            )
        ]
        if country_code:
            reviewable = [c for c in reviewable if c.proposed_country_code == country_code.upper()]
        if category:
            reviewable = [c for c in reviewable if c.proposed_category == category]
        return reviewable

    def get_candidate_by_id(self, candidate_id: str) -> Optional[ImportCandidate]:
        """Find a single candidate across all staged batches."""
        for c in self.repository.load_all_candidates():
            if c.candidate_id == candidate_id:
                return c
        return None

    def review_candidate(
        self,
        candidate_id: str,
        curator: str,
        approved: bool,
        notes: str,
        rights_status: Optional[RightsStatusEnum] = None,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
        proposed_summary: Optional[str] = None,
    ) -> Optional[ImportCandidate]:
        """Record an editorial review decision for a candidate."""
        candidate = self.get_candidate_by_id(candidate_id)
        if not candidate:
            return None

        candidate.reviewed_by = curator
        candidate.reviewed_at = datetime.now(timezone.utc)
        candidate.review_notes = notes

        if rights_status:
            candidate.rights_status = rights_status
        if proposed_country_code:
            candidate.proposed_country_code = proposed_country_code.upper()
        if proposed_category:
            candidate.proposed_category = proposed_category
        if proposed_summary:
            candidate.proposed_summary = proposed_summary

        if approved:
            candidate.disposition = CandidateDispositionEnum.APPROVED_FOR_PUBLICATION
            candidate.verification_status = VerificationStatusEnum.VERIFIED
        else:
            candidate.disposition = CandidateDispositionEnum.REJECTED
            candidate.verification_status = VerificationStatusEnum.REJECTED

        # Save back to batch file
        self._update_candidate_in_batch(candidate)
        return candidate

    def _update_candidate_in_batch(self, updated: ImportCandidate) -> None:
        """Helper to atomically update a candidate within its batch file."""
        batch_id = updated.import_batch_id
        candidates = self.repository.load_batch(batch_id)
        new_list = [updated if c.candidate_id == updated.candidate_id else c for c in candidates]
        meta = self.repository.get_batch_metadata(batch_id)
        self.repository.save_batch(batch_id, new_list, meta)

    def promote_candidate_to_story(
        self,
        candidate: ImportCandidate,
        story_id: str,
        summary: str,
        sources: list[StorySource],
        title: Optional[str] = None,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        subtype: Optional[str] = None,
        motifs: Optional[list[str]] = None,
        themes: Optional[list[str]] = None,
        historical_period: Optional[str] = None,
        region_or_community: Optional[str] = None,
        community_attributions: Optional[list[str]] = None,
        geographic_associations: Optional[list[str]] = None,
        rights_status: Optional[RightsStatusEnum] = None,
        attribution_text: Optional[str] = None,
    ) -> StoryRecord:
        """Transform an approved ImportCandidate into a canonical StoryRecord."""
        final_country = (country_code or candidate.proposed_country_code or "UN").upper()
        final_category = category or candidate.proposed_category or CategoryEnum.FOLKLORE
        final_title = title or candidate.raw_title
        final_rights = rights_status or candidate.rights_status

        # Validate summary
        summary_valid, issues = self.builder.validate_summary_text(summary)
        if not summary_valid:
            raise ValueError(f"Summary validation failed: {'; '.join(issues)}")

        record = StoryRecord(
            id=story_id,
            schema_version="2.0.0",
            record_version="1.0.0",
            title=final_title,
            country_code=final_country,
            category=final_category,
            subtype=subtype,
            summary=summary.strip(),
            alternate_names=[],
            language="en",
            alternate_languages=[candidate.raw_language] if candidate.raw_language else [],
            motifs=motifs or [],
            themes=themes or [],
            historical_period=historical_period,
            region_or_community=region_or_community,
            community_attributions=community_attributions or [],
            geographic_associations=geographic_associations or [],
            sources=sources,
            license="Public Domain / Open Access Educational Use",
            rights_status=final_rights,
            attribution_text=attribution_text,
            canonical_url=candidate.raw_url,
            verification_status=VerificationStatusEnum.VERIFIED,
            content_origin=ContentOriginEnum.ORIGINAL_SUMMARY,
        )

        return record

    def validate_for_publication(self, record: StoryRecord) -> PublicationEligibilityResult:
        """Evaluate a StoryRecord against KathaYantra's publication policy."""
        return self.policy.evaluate_eligibility(record)

    def audit_record(self, record: StoryRecord) -> SourceVerificationResult:
        """Run full source verification audit on a StoryRecord."""
        return self.verification_service.verify_story_record(record)


curation_service = CurationService()

