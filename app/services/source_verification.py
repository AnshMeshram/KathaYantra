"""Source Verification and Provenance Inspection Service for KathaYantra.

Provides automated and curatorial evaluation of source credibility, rights clearances,
cultural attribution completeness, and anti-hallucination narrative validity.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)


class SourceInspectionItem(BaseModel):
    """Evaluation result for an individual source citation."""

    source_id: Optional[str] = None
    title_or_name: str
    url: Optional[str] = None
    url_valid: bool
    rights_status: RightsStatusEnum
    attribution_required: bool
    attribution_satisfied: bool
    notes: list[str] = Field(default_factory=list)


class SourceVerificationResult(BaseModel):
    """Comprehensive verification result for a candidate or published record."""

    target_id: str
    is_verified: bool
    verification_tier: str = Field(
        default="none",
        description="'full_text', 'metadata_only', or 'rejected'",
    )
    narrative_valid: bool
    cultural_attribution_valid: bool
    rights_cleared: bool
    sources_verified: bool
    source_inspections: list[SourceInspectionItem] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SourceVerificationService:
    """Service to audit source citations, rights clearances, and cultural attribution."""

    MIN_SUMMARY_WORDS: int = 15
    TARGET_SUMMARY_MIN_WORDS: int = 50
    TARGET_SUMMARY_MAX_WORDS: int = 250

    SUSPICIOUS_PHRASES: list[str] = [
        "as an ai",
        "as a language model",
        "i do not have personal",
        "lorem ipsum",
        "insert story here",
        "todo: add summary",
        "fictional ai story",
    ]

    def verify_source(self, source: StorySource, record_attribution: Optional[str] = None) -> SourceInspectionItem:
        """Inspect a single source citation for validity and licensing clearance."""
        notes: list[str] = []
        name = source.title or source.name or source.id or "Unnamed Source"

        url_valid = bool(source.url and source.url.startswith(("http://", "https://")))
        if not url_valid:
            notes.append(f"Source '{name}' lacks a valid HTTP/HTTPS URL.")

        attribution_satisfied = True
        if source.attribution_required:
            if not (source.attribution_text or record_attribution):
                attribution_satisfied = False
                notes.append(f"Source '{name}' requires attribution, but no attribution text is supplied.")

        return SourceInspectionItem(
            source_id=source.id,
            title_or_name=name,
            url=source.url,
            url_valid=url_valid,
            rights_status=source.rights_status,
            attribution_required=source.attribution_required,
            attribution_satisfied=attribution_satisfied,
            notes=notes,
        )

    def check_narrative_validity(self, summary: Optional[str], content_origin: Optional[ContentOriginEnum] = None) -> tuple[bool, list[str]]:
        """Validate that narrative text is authentic, substantial, and not synthetic AI hallucination."""
        findings: list[str] = []

        if not summary or not summary.strip():
            findings.append("Summary is empty or missing.")
            return False, findings

        summary_clean = summary.strip()
        word_count = len(summary_clean.split())

        if word_count < self.MIN_SUMMARY_WORDS:
            findings.append(f"Summary contains only {word_count} words; minimum required is {self.MIN_SUMMARY_WORDS}.")

        # Check for suspicious hallucination phrases
        summary_lower = summary_clean.lower()
        for phrase in self.SUSPICIOUS_PHRASES:
            if phrase in summary_lower:
                findings.append(f"Summary contains suspicious or synthetic phrase: '{phrase}'.")

        if content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
            findings.append("Content origin is classified as AI-generated fiction; forbidden in folklore archive.")

        narrative_valid = len(findings) == 0
        return narrative_valid, findings

    def check_cultural_attribution(self, country_code: Optional[str], region_or_community: Optional[str], community_attributions: list[str]) -> tuple[bool, list[str]]:
        """Check cultural attribution and regional specificity."""
        findings: list[str] = []

        if not country_code or country_code.upper() not in SUPPORTED_COUNTRY_CODES:
            findings.append(f"Country code '{country_code}' is missing or not supported.")

        if not region_or_community and not community_attributions:
            findings.append("Cultural attribution is weak: neither region_or_community nor community_attributions is specified.")

        cultural_valid = len(findings) == 0
        return cultural_valid, findings

    def verify_story_record(self, record: StoryRecord) -> SourceVerificationResult:
        """Verify an existing or proposed StoryRecord."""
        findings: list[str] = []
        recommendations: list[str] = []
        source_inspections: list[SourceInspectionItem] = []

        # 1. Sources check
        sources_verified = True
        if not record.sources:
            sources_verified = False
            findings.append("Record does not include any source citations.")
        else:
            for s in record.sources:
                inspection = self.verify_source(s, record.attribution_text)
                source_inspections.append(inspection)
                if not inspection.url_valid:
                    sources_verified = False
                    findings.extend(inspection.notes)
                if not inspection.attribution_satisfied:
                    sources_verified = False
                    findings.extend(inspection.notes)

        # 2. Rights check
        rights_cleared = False
        tier = "none"
        if record.rights_status in (RightsStatusEnum.APPROVED, RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED):
            rights_cleared = True
            tier = "full_text"
        elif record.rights_status == RightsStatusEnum.METADATA_ONLY:
            if not record.long_description or len(record.long_description.strip()) == 0:
                rights_cleared = True
                tier = "metadata_only"
            else:
                findings.append("Rights status is metadata_only, but record contains full-text long_description.")
        else:
            findings.append(f"Rights status '{record.rights_status.value}' is not cleared for publication.")

        # 3. Narrative check
        narrative_valid, narrative_findings = self.check_narrative_validity(record.summary, record.content_origin)
        findings.extend(narrative_findings)

        # 4. Cultural attribution check
        cultural_valid, cultural_findings = self.check_cultural_attribution(
            record.country_code, record.region_or_community, record.community_attributions
        )
        findings.extend(cultural_findings)

        is_verified = (
            sources_verified
            and rights_cleared
            and narrative_valid
            and cultural_valid
            and record.verification_status == VerificationStatusEnum.VERIFIED
        )

        if not is_verified:
            tier = "none"
            recommendations.append("Address flagged findings before approving for public dataset envelope.")

        return SourceVerificationResult(
            target_id=record.id,
            is_verified=is_verified,
            verification_tier=tier,
            narrative_valid=narrative_valid,
            cultural_attribution_valid=cultural_valid,
            rights_cleared=rights_cleared,
            sources_verified=sources_verified,
            source_inspections=source_inspections,
            findings=findings,
            recommendations=recommendations,
        )

    def verify_candidate(self, candidate: ImportCandidate) -> SourceVerificationResult:
        """Evaluate an import candidate during staging and triage."""
        findings: list[str] = []
        recommendations: list[str] = []
        source_inspections: list[SourceInspectionItem] = []

        # Source URL check
        url_valid = bool(candidate.raw_url and candidate.raw_url.startswith(("http://", "https://")))
        if not url_valid:
            findings.append(f"Candidate raw_url '{candidate.raw_url}' is missing or not a valid HTTP/HTTPS URL.")

        source_inspections.append(
            SourceInspectionItem(
                source_id=candidate.source_registry_id,
                title_or_name=candidate.raw_title,
                url=candidate.raw_url,
                url_valid=url_valid,
                rights_status=candidate.rights_status,
                attribution_required=False,
                attribution_satisfied=True,
                notes=findings.copy(),
            )
        )

        sources_verified = url_valid
        rights_cleared = candidate.rights_status in (
            RightsStatusEnum.APPROVED,
            RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED,
            RightsStatusEnum.METADATA_ONLY,
        )
        if not rights_cleared:
            findings.append(f"Candidate rights status is '{candidate.rights_status.value}' (unverified).")

        narrative_valid, narrative_findings = self.check_narrative_validity(candidate.proposed_summary)
        findings.extend(narrative_findings)

        cultural_valid = bool(
            candidate.proposed_country_code and candidate.proposed_country_code.upper() in SUPPORTED_COUNTRY_CODES
        )
        if not cultural_valid:
            findings.append(f"Candidate proposed_country_code '{candidate.proposed_country_code}' is invalid or missing.")

        is_verified = sources_verified and rights_cleared and narrative_valid and cultural_valid

        tier = "none"
        if is_verified:
            tier = "full_text" if candidate.rights_status != RightsStatusEnum.METADATA_ONLY else "metadata_only"
        else:
            recommendations.append("Candidate requires editorial curation and rights review.")

        return SourceVerificationResult(
            target_id=candidate.candidate_id,
            is_verified=is_verified,
            verification_tier=tier,
            narrative_valid=narrative_valid,
            cultural_attribution_valid=cultural_valid,
            rights_cleared=rights_cleared,
            sources_verified=sources_verified,
            source_inspections=source_inspections,
            findings=findings,
            recommendations=recommendations,
        )


source_verification_service = SourceVerificationService()
