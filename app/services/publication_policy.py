"""Publication Eligibility Policy Service for KathaYantra.

Provides deterministic evaluation of whether a StoryRecord meets all curatorial,
legal, provenance, and anti-hallucination criteria for public archive dissemination.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.source import RightsStatusEnum
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)


class PublicationEligibilityResult(BaseModel):
    """Result object indicating whether a story record is eligible for public archive display."""

    record_id: str
    is_eligible: bool
    reasons: list[str] = Field(default_factory=list, description="Passed policy requirements")
    violations: list[str] = Field(default_factory=list, description="Failed requirements blocking publication")
    publication_tier: str = Field(
        default="none",
        description="Allowed publication tier: 'full_text', 'metadata_only', or 'none'",
    )


class PublicationPolicy:
    """Deterministic policy engine evaluating story records for public dissemination."""

    MIN_SUMMARY_LENGTH: int = 15

    @classmethod
    def evaluate_eligibility(cls, record: StoryRecord) -> PublicationEligibilityResult:
        """Evaluate a StoryRecord against KathaYantra's strict publication rules."""
        violations: list[str] = []
        reasons: list[str] = []
        tier = "none"

        # 1. Structural & Schema Integrity
        if not record.id:
            violations.append("Record is missing an identifier.")
        elif not (record.id.startswith(record.country_code) and ("-FOLK-" in record.id or "-URBAN-" in record.id)):
            violations.append(f"Record ID '{record.id}' prefix does not match country_code '{record.country_code}' and category.")
        else:
            reasons.append("ID adheres to canonical pattern and country/category prefix.")

        # 2. Country Association
        if record.country_code not in SUPPORTED_COUNTRY_CODES:
            violations.append(f"Country code '{record.country_code}' is not supported.")
        else:
            reasons.append(f"Country code '{record.country_code}' is supported ({SUPPORTED_COUNTRY_CODES[record.country_code]}).")

        # 3. Content Origin & Anti-Fiction Rule
        if record.content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
            violations.append("Record contains AI-generated synthetic fiction; rejected from authentic folklore archives.")
        else:
            reasons.append(f"Content origin is authentic ({record.content_origin.value}).")

        # 4. Summary Completeness
        if not record.summary or len(record.summary.strip()) < cls.MIN_SUMMARY_LENGTH:
            violations.append(f"Summary must be an original narrative synopsis of at least {cls.MIN_SUMMARY_LENGTH} characters.")
        else:
            reasons.append("Summary is complete and meets minimum narrative length.")

        # 5. Provenance & Sources
        if not record.sources:
            violations.append("At least one traceable bibliographic source citation is mandatory.")
        else:
            valid_sources = [s for s in record.sources if s.url and s.url.startswith(("http://", "https://"))]
            if not valid_sources:
                violations.append("All provided source citations lack valid HTTP/HTTPS URLs.")
            else:
                reasons.append(f"{len(valid_sources)} valid traceable source citation(s) documented.")

        # 6. Verification Status Requirement
        if record.verification_status != VerificationStatusEnum.VERIFIED:
            violations.append(
                f"Verification status is '{record.verification_status.value}'; record must be 'verified' by an editor to publish."
            )
        else:
            reasons.append("Curatorial verification status is verified.")

        # 7. Rights & Redistribution Status Enforcement
        if record.rights_status in (
            RightsStatusEnum.NEEDS_RIGHTS_REVIEW,
            RightsStatusEnum.PERMISSION_REQUIRED,
            RightsStatusEnum.RESTRICTED,
            RightsStatusEnum.UNKNOWN,
        ):
            violations.append(
                f"Rights status '{record.rights_status.value}' prohibits public dissemination. "
                "Changing verification status alone does NOT bypass rights clearance."
            )
        elif record.rights_status == RightsStatusEnum.METADATA_ONLY:
            # Metadata-only records must NOT contain full-text payload
            if record.long_description and len(record.long_description.strip()) > 0:
                violations.append(
                    "Record is classified as 'metadata_only' but contains a full-text long_description payload. "
                    "Full text must be removed or cleared before metadata publication."
                )
            else:
                tier = "metadata_only"
                reasons.append("Metadata-only publication cleared; no restricted full text included.")
        elif record.rights_status in (RightsStatusEnum.APPROVED, RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED):
            tier = "full_text"
            reasons.append(f"Full rights cleared under status '{record.rights_status.value}'.")

        # 8. Mandatory Attribution Check
        for s in record.sources:
            if s.attribution_required and not (s.attribution_text or record.attribution_text):
                violations.append(
                    f"Source '{s.title or s.name}' requires explicit attribution, but neither record nor source provides attribution_text."
                )

        is_eligible = len(violations) == 0

        return PublicationEligibilityResult(
            record_id=record.id,
            is_eligible=is_eligible,
            reasons=reasons,
            violations=violations,
            publication_tier=tier if is_eligible else "none",
        )


publication_policy = PublicationPolicy()
