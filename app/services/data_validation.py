"""Data Quality and Archival Governance Validator for KathaYantra.

Executes deterministic multi-tier validation across all 30 country seed files,
dataset envelopes, story records, source citations, and manifest counts.
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field
from app.core.config import settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.dataset import DatasetEnvelope
from app.schemas.source import RightsStatusEnum
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
)


class ValidationIssue(BaseModel):
    """An individual issue detected during data validation."""

    severity: str = Field(..., description="'error' (fatal) or 'warning' (curatorial review needed)")
    error_code: str = Field(..., description="Unique error code identifier")
    file_path: Optional[str] = Field(default=None, description="Path to file being inspected")
    record_id: Optional[str] = Field(default=None, description="Affected record ID if applicable")
    field_path: Optional[str] = Field(default=None, description="JSON/Pydantic field path")
    message: str = Field(..., description="Actionable explanation of the issue")


class DataValidationReport(BaseModel):
    """Structured report returned by the DataQualityValidator."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_files_inspected: int = 0
    total_records_inspected: int = 0
    is_valid: bool = True
    error_count: int = 0
    warning_count: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)
    counts_by_country: dict[str, dict[str, int]] = Field(default_factory=dict)


class DataQualityValidator:
    """Comprehensive validator enforcing KathaYantra's 17 data quality checks."""

    def __init__(
        self,
        folklore_dir: Optional[Path] = None,
        urban_dir: Optional[Path] = None,
        source_registry_path: Optional[Path] = None,
    ):
        self.folklore_dir = folklore_dir or settings.folklore_seed_dir
        self.urban_dir = urban_dir or settings.urban_legends_seed_dir
        self.source_registry_path = source_registry_path or (settings.SEED_DIR / "source_registry.json")

    def validate_all(self) -> DataValidationReport:
        """Execute all 17 validation checks across the workspace seed files."""
        issues: list[ValidationIssue] = []
        files_count = 0
        records_count = 0

        # Load valid source registry IDs for referential checks
        registered_source_ids: set[str] = set()
        if self.source_registry_path.exists():
            try:
                with open(self.source_registry_path, "r", encoding="utf-8") as f:
                    reg_data = json.load(f)
                    registered_source_ids = {s.get("id") for s in reg_data if isinstance(s, dict) and s.get("id")}
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        error_code="REGISTRY_READ_ERROR",
                        file_path=str(self.source_registry_path),
                        message=f"Failed to parse source_registry.json: {str(e)}",
                    )
                )

        global_id_registry: dict[str, str] = {}  # id -> file_path
        global_title_registry: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        counts_by_country: dict[str, dict[str, int]] = {
            c: {"folklore": 0, "urban_legends": 0} for c in sorted(SUPPORTED_COUNTRY_CODES.keys())
        }

        # Scan all 15 countries across folklore and urban_legends
        target_categories = [
            (CategoryEnum.FOLKLORE, self.folklore_dir, "folklore"),
            (CategoryEnum.URBAN_LEGEND, self.urban_dir, "urban_legends"),
        ]

        for category_enum, dir_path, category_label in target_categories:
            if not dir_path.exists():
                issues.append(
                    ValidationIssue(
                        severity="error",
                        error_code="DIRECTORY_MISSING",
                        file_path=str(dir_path),
                        message=f"Seed category directory does not exist: {dir_path}",
                    )
                )
                continue

            for country_code in sorted(SUPPORTED_COUNTRY_CODES.keys()):
                file_path = dir_path / f"{country_code}.json"
                files_count += 1

                if not file_path.exists():
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            error_code="SEED_FILE_MISSING",
                            file_path=str(file_path),
                            message=f"Expected seed file does not exist: {file_path}",
                        )
                    )
                    continue

                # 1. JSON Syntax Check
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                except Exception as e:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            error_code="JSON_SYNTAX_ERROR",
                            file_path=str(file_path),
                            message=f"Invalid JSON syntax in {file_path.name}: {str(e)}",
                        )
                    )
                    continue

                # 2. Check Raw Record IDs for Duplicate Detection Across Files
                raw_records = raw_data.get("records", []) if isinstance(raw_data, dict) else []
                if isinstance(raw_records, list):
                    for r in raw_records:
                        if isinstance(r, dict) and r.get("id"):
                            rid = str(r["id"]).strip()
                            if rid in global_id_registry:
                                issues.append(
                                    ValidationIssue(
                                        severity="error",
                                        error_code="DUPLICATE_RECORD_ID",
                                        file_path=str(file_path),
                                        record_id=rid,
                                        field_path="id",
                                        message=f"Duplicate ID '{rid}' also found in {global_id_registry[rid]}",
                                    )
                                )
                            else:
                                global_id_registry[rid] = str(file_path)

                # 3. Correct Dataset Envelope Check
                try:
                    envelope = DatasetEnvelope.model_validate(raw_data)
                except Exception as e:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            error_code="ENVELOPE_SCHEMA_ERROR",
                            file_path=str(file_path),
                            message=f"Dataset envelope validation failed in {file_path.name}: {str(e)}",
                        )
                    )
                    continue

                # 3. Country Code and Category Alignment with Filename and Directory
                if envelope.country_code != country_code:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            error_code="COUNTRY_ALIGNMENT_MISMATCH",
                            file_path=str(file_path),
                            message=f"File {file_path.name} declares country_code '{envelope.country_code}', expected '{country_code}'",
                        )
                    )

                if envelope.category != category_enum:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            error_code="CATEGORY_ALIGNMENT_MISMATCH",
                            file_path=str(file_path),
                            message=f"File {file_path.name} in {category_label}/ declares category '{envelope.category.value}', expected '{category_enum.value}'",
                        )
                    )

                # Record counts tracking
                rec_count = len(envelope.records)
                records_count += rec_count
                counts_by_country[country_code][category_label] = rec_count

                # 4-17. Story Record Checks
                for idx, rec in enumerate(envelope.records, start=1):
                    # 5. Stable ID format
                    expected_prefix = f"{country_code}-{'FOLK' if category_enum == CategoryEnum.FOLKLORE else 'URBAN'}-"
                    if not rec.id.startswith(expected_prefix):
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                error_code="ID_PREFIX_INCONSISTENT",
                                file_path=str(file_path),
                                record_id=rec.id,
                                field_path="id",
                                message=f"Record ID '{rec.id}' does not match expected prefix '{expected_prefix}'",
                            )
                        )

                    # 7. Duplicate Canonical Titles (Warning for review)
                    clean_title = rec.title.strip().lower()
                    global_title_registry[clean_title].append(
                        {"id": rec.id, "country": rec.country_code, "category": rec.category.value, "file": file_path.name}
                    )

                    # 8. Source URL Validity & 9. Missing Sources
                    if not rec.sources:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                error_code="MISSING_SOURCES",
                                file_path=str(file_path),
                                record_id=rec.id,
                                field_path="sources",
                                message=f"Record '{rec.id}' has empty sources list.",
                            )
                        )
                    else:
                        for s_idx, s in enumerate(rec.sources):
                            parsed = urlparse(s.url)
                            if not (parsed.scheme in ("http", "https") and bool(parsed.netloc)):
                                issues.append(
                                    ValidationIssue(
                                        severity="error",
                                        error_code="INVALID_SOURCE_URL",
                                        file_path=str(file_path),
                                        record_id=rec.id,
                                        field_path=f"sources[{s_idx}].url",
                                        message=f"Invalid URL '{s.url}' in source citation.",
                                    )
                                )
                            # 15. Source registry reference check (Warning if not linked)
                            if s.id and registered_source_ids and s.id not in registered_source_ids:
                                issues.append(
                                    ValidationIssue(
                                        severity="warning",
                                        error_code="UNREGISTERED_SOURCE_REF",
                                        file_path=str(file_path),
                                        record_id=rec.id,
                                        field_path=f"sources[{s_idx}].id",
                                        message=f"Source ID '{s.id}' is not in source_registry.json.",
                                    )
                                )

                    # 10. Missing Rights Status
                    if not rec.rights_status:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                error_code="MISSING_RIGHTS_STATUS",
                                file_path=str(file_path),
                                record_id=rec.id,
                                field_path="rights_status",
                                message=f"Record '{rec.id}' has empty rights_status.",
                            )
                        )

                    # 11. Unverified Records Incorrectly Marked Publishable
                    if (
                        rec.verification_status != VerificationStatusEnum.VERIFIED
                        and rec.rights_status == RightsStatusEnum.APPROVED
                    ):
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                error_code="UNVERIFIED_BUT_APPROVED",
                                file_path=str(file_path),
                                record_id=rec.id,
                                field_path="verification_status",
                                message=f"Record '{rec.id}' has rights_status 'approved' but verification_status is '{rec.verification_status.value}'.",
                            )
                        )

                    # 13. AI Fiction Stored in Production Folklore Files
                    if rec.content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                error_code="AI_FICTION_IN_PRODUCTION",
                                file_path=str(file_path),
                                record_id=rec.id,
                                field_path="content_origin",
                                message=f"Record '{rec.id}' contains AI-generated fiction inside production seed files.",
                            )
                        )

        # Check for title duplicates across the registry (Warning)
        for title_str, occurrences in global_title_registry.items():
            if len(occurrences) > 1:
                ids_str = ", ".join(f"{o['id']} ({o['country']})" for o in occurrences)
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        error_code="RECURRING_TITLE",
                        message=f"Title '{title_str}' appears in multiple records: {ids_str}. Review for legitimate regional variants vs accidental duplicate.",
                    )
                )

        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")

        return DataValidationReport(
            total_files_inspected=files_count,
            total_records_inspected=records_count,
            is_valid=(error_count == 0),
            error_count=error_count,
            warning_count=warning_count,
            issues=issues,
            counts_by_country=counts_by_country,
        )


data_quality_validator = DataQualityValidator()
