"""Comprehensive Ingestion and Coverage Reporting Service for KathaYantra."""

from typing import Any, Optional
from app.core.config import settings
from app.repositories.candidate_repository import CandidateRepository, candidate_repository
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.story import CategoryEnum
from app.services.manifest_service import ManifestService, manifest_service


class ImportReportingService:
    """Generates auditable coverage summaries distinguishing staged candidates from published stories."""

    def __init__(
        self,
        repository: Optional[CandidateRepository] = None,
        manifest_srv: Optional[ManifestService] = None,
    ):
        self.repository = repository or candidate_repository
        self.manifest_service = manifest_srv or manifest_service

    def generate_coverage_report(self) -> dict[str, Any]:
        """Aggregate all candidate files and compare against 300-record target quotas."""
        candidates = self.repository.load_all_candidates()
        published_manifest = self.manifest_service.load_manifest()

        # Disposition counts
        disposition_counts = {d.value: 0 for d in CandidateDispositionEnum}
        source_counts: dict[str, int] = {}
        country_counts: dict[str, dict[str, int]] = {
            c: {"folklore": 0, "urban_legend": 0, "total": 0} for c in SUPPORTED_COUNTRY_CODES
        }
        unmapped_country_count = 0

        for cand in candidates:
            # Disposition
            disp_val = cand.disposition.value
            disposition_counts[disp_val] = disposition_counts.get(disp_val, 0) + 1

            # Source
            src = cand.source_registry_id or "unknown"
            source_counts[src] = source_counts.get(src, 0) + 1

            # Country & category
            c_code = cand.proposed_country_code
            if c_code and c_code in country_counts:
                cat = cand.proposed_category.value if cand.proposed_category else "folklore"
                if cat in country_counts[c_code]:
                    country_counts[c_code][cat] += 1
                country_counts[c_code]["total"] += 1
            else:
                unmapped_country_count += 1

        # Country coverage gap against targets (10 folklore + 10 urban legends per country)
        gaps: dict[str, dict[str, int]] = {}
        for c in SUPPORTED_COUNTRY_CODES:
            pub_folk = published_manifest.folklore_counts_by_country.get(c, 0)
            pub_urban = published_manifest.urban_legend_counts_by_country.get(c, 0)
            staged_folk = country_counts[c]["folklore"]
            staged_urban = country_counts[c]["urban_legend"]

            gaps[c] = {
                "target_folklore": 10,
                "published_folklore": pub_folk,
                "staged_candidate_folklore": staged_folk,
                "folklore_shortfall": max(0, 10 - pub_folk),
                "target_urban_legends": 10,
                "published_urban_legends": pub_urban,
                "staged_candidate_urban_legends": staged_urban,
                "urban_legends_shortfall": max(0, 10 - pub_urban),
            }

        total_staged = len(candidates)
        published_total = published_manifest.actual_record_count

        return {
            "summary": {
                "total_staged_candidates": total_staged,
                "total_published_verified_stories": published_total,
                "required_catalogue_target": settings.REQUIRED_TOTAL_RECORDS,
                "published_remaining_gap": max(0, settings.REQUIRED_TOTAL_RECORDS - published_total),
                "unmapped_country_candidates": unmapped_country_count,
            },
            "disposition_breakdown": disposition_counts,
            "source_breakdown": source_counts,
            "country_matrix": gaps,
        }

    def format_text_report(self) -> str:
        """Format a human-readable CLI summary table."""
        report = self.generate_coverage_report()
        summary = report["summary"]
        disp = report["disposition_breakdown"]
        matrix = report["country_matrix"]

        lines = [
            "=" * 78,
            "  KATHAYANTRA — INGESTION PIPELINE & CANDIDATE COVERAGE REPORT",
            "=" * 78,
            f"Total Candidates Staged:         {summary['total_staged_candidates']}",
            f"Published Verified Stories:       {summary['total_published_verified_stories']} (Target: {summary['required_catalogue_target']})",
            f"Unmapped / Pending Review:        {summary['unmapped_country_candidates']}",
            "-" * 78,
            "Candidate Disposition Breakdown:",
            f"  - New Candidates:               {disp.get('new_candidate', 0)}",
            f"  - Needs Mapping Review:         {disp.get('needs_mapping_review', 0)}",
            f"  - Needs Source Verification:    {disp.get('needs_source_verification', 0)}",
            f"  - Needs Rights Review:          {disp.get('needs_rights_review', 0)}",
            f"  - Eligible for Editorial Review:{disp.get('eligible_for_editorial_review', 0)}",
            f"  - Approved for Publication:     {disp.get('approved_for_publication', 0)}",
            f"  - Duplicate Candidates:         {disp.get('duplicate_candidate', 0)}",
            f"  - Rejected:                     {disp.get('rejected', 0)}",
            "-" * 78,
            "Country Matrix (Published Verified vs Staged Candidates vs Target 10+10):",
            " Code | Folklore (Pub / Staged) | Urban Legends (Pub / Staged) | Target Shortfall",
            "------+-------------------------+------------------------------+-----------------",
        ]

        for code in sorted(SUPPORTED_COUNTRY_CODES):
            m = matrix[code]
            folk_str = f"{m['published_folklore']} / {m['staged_candidate_folklore']}"
            urban_str = f"{m['published_urban_legends']} / {m['staged_candidate_urban_legends']}"
            shortfall = m["folklore_shortfall"] + m["urban_legends_shortfall"]
            lines.append(f"  {code}  | {folk_str:^23} | {urban_str:^28} | {shortfall:^15}")

        lines.extend([
            "=" * 78,
            "Note: Staged candidates are held in data/processed/candidates/ and are NOT",
            "counted as verified published stories until curatorial and rights clearance.",
            "=" * 78,
        ])
        return "\n".join(lines)


import_reporting_service = ImportReportingService()
