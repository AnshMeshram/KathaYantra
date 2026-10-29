"""Manifest Service for KathaYantra Dataset Audit and Integrity Checking.

Dynamically scans the seed dataset folders (data/seed/folklore and data/seed/urban_legends)
and computes actual counts, country coverage, rights status, and verification progress.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.manifest import ActualCounts, DatasetManifest, TargetBreakdown
from app.schemas.story import RightsStatusEnum, VerificationStatusEnum


class ManifestService:
    """Service to compute and validate the dataset manifest from real files."""

    def __init__(
        self,
        folklore_dir: Optional[Path] = None,
        urban_dir: Optional[Path] = None,
        manifest_file: Optional[Path] = None,
    ):
        self.folklore_dir = folklore_dir or settings.folklore_seed_dir
        self.urban_dir = urban_dir or settings.urban_legends_seed_dir
        self.manifest_file = manifest_file or (settings.MANIFESTS_DIR / "dataset_manifest.json")

    def compute_manifest(self) -> DatasetManifest:
        """Scan seed directory files and compute true actual counts."""
        country_codes = sorted(list(SUPPORTED_COUNTRY_CODES.keys()))

        folklore_counts: dict[str, int] = {c: 0 for c in country_codes}
        urban_legend_counts: dict[str, int] = {c: 0 for c in country_codes}

        total_folklore = 0
        total_urban = 0
        unverified_count = 0
        rights_pending_count = 0
        active_sources: set[str] = set()

        # Scan folklore
        if self.folklore_dir.exists():
            for c in country_codes:
                file_path = self.folklore_dir / f"{c}.json"
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            records = data.get("records", [])
                            count = len(records)
                            folklore_counts[c] = count
                            total_folklore += count
                            for r in records:
                                if r.get("verification_status") != VerificationStatusEnum.VERIFIED.value:
                                    unverified_count += 1
                                if r.get("rights_status") in (
                                    RightsStatusEnum.NEEDS_RIGHTS_REVIEW.value,
                                    RightsStatusEnum.PERMISSION_REQUIRED.value,
                                    RightsStatusEnum.UNKNOWN.value,
                                ):
                                    rights_pending_count += 1
                                for s in r.get("sources", []):
                                    if isinstance(s, dict) and s.get("name"):
                                        active_sources.add(s["name"])
                    except Exception:
                        pass

        # Scan urban legends
        if self.urban_dir.exists():
            for c in country_codes:
                file_path = self.urban_dir / f"{c}.json"
                if file_path.exists():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            records = data.get("records", [])
                            count = len(records)
                            urban_legend_counts[c] = count
                            total_urban += count
                            for r in records:
                                if r.get("verification_status") != VerificationStatusEnum.VERIFIED.value:
                                    unverified_count += 1
                                if r.get("rights_status") in (
                                    RightsStatusEnum.NEEDS_RIGHTS_REVIEW.value,
                                    RightsStatusEnum.PERMISSION_REQUIRED.value,
                                    RightsStatusEnum.UNKNOWN.value,
                                ):
                                    rights_pending_count += 1
                                for s in r.get("sources", []):
                                    if isinstance(s, dict) and s.get("name"):
                                        active_sources.add(s["name"])
                    except Exception:
                        pass

        manifest = DatasetManifest(
            dataset_version=settings.PROJECT_VERSION,
            country_list=country_codes,
            required_record_count=settings.REQUIRED_TOTAL_RECORDS,
            target_breakdown=TargetBreakdown(
                per_country_folklore=settings.TARGET_FOLKLORE_PER_COUNTRY,
                per_country_urban_legends=settings.TARGET_URBAN_LEGENDS_PER_COUNTRY,
                total_countries=settings.TARGET_COUNTRIES_COUNT,
            ),
            current_actual_counts=ActualCounts(
                total_records=total_folklore + total_urban,
                folklore_records=total_folklore,
                urban_legend_records=total_urban,
            ),
            folklore_counts_by_country=folklore_counts,
            urban_legend_counts_by_country=urban_legend_counts,
            unverified_records=unverified_count,
            rights_pending_records=rights_pending_count,
            source_coverage=sorted(list(active_sources)),
            last_validation_timestamp=datetime.now(timezone.utc).isoformat(),
            dataset_limitations=[
                "Phase 1 Foundation: Actual published record count is currently 0. The target is 300 records (15 countries * 20 records).",
                "Raw CSV (folk_tales_deduplicated.csv) contains 2,938 records under review and is restricted to data/raw pending individual rights clearance.",
                "External APIs (LOC, Wikimedia, Europeana, etc.) are registered in data/seed/source_registry.json for Phase 2 integration.",
                "No synthetic AI stories are accepted into seed folklore files without explicit ai_generated_fiction classification."
            ],
        )

        return manifest

    def save_manifest(self) -> Path:
        """Compute manifest and write to data/manifests/dataset_manifest.json."""
        manifest = self.compute_manifest()
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))
        return self.manifest_file


manifest_service = ManifestService()

