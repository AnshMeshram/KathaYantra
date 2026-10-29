"""KathaYantra — Verified Dataset Builder and Seed Population CLI.

Evaluates curated story records against KathaYantra's strict PublicationPolicy,
wraps them into versioned DatasetEnvelope schemas, atomically writes
folklore and urban-legend seed files, and updates the dataset manifest.

Usage:
    python scripts/build_verified_dataset.py [--country IN] [--dry-run] [--verbose]
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Optional

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.curation.registry import get_curated_records_for_country, get_all_curated_records
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.dataset import DatasetEnvelope, DatasetMetadata
from app.schemas.story import CategoryEnum, StoryRecord
from app.services.manifest_service import manifest_service
from app.services.publication_policy import publication_policy


def build_and_publish_partition(
    country_code: str,
    category: CategoryEnum,
    records: list[StoryRecord],
    dry_run: bool = False,
    verbose: bool = False,
) -> tuple[int, list[str]]:
    """Validate records against PublicationPolicy, wrap in DatasetEnvelope, and persist."""
    violations_log: list[str] = []
    eligible_records: list[StoryRecord] = []

    for rec in records:
        result = publication_policy.evaluate_eligibility(rec)
        if not result.is_eligible:
            msg = f"Record '{rec.id}' failed publication policy: {'; '.join(result.violations)}"
            violations_log.append(msg)
            if verbose:
                print(f"  [POLICY REJECT] {msg}")
        else:
            eligible_records.append(rec)

    # Determine target directory
    target_dir = settings.folklore_seed_dir if category == CategoryEnum.FOLKLORE else settings.urban_legends_seed_dir
    file_path = target_dir / f"{country_code}.json"

    envelope = DatasetEnvelope(
        schema_version="2.0.0",
        dataset_id=f"{country_code}-{category.value}",
        country_code=country_code,
        category=category,
        records=eligible_records,
        metadata=DatasetMetadata(
            description=f"Curated {category.value} dataset for {SUPPORTED_COUNTRY_CODES[country_code]}",
            dataset_version="2.0.0",
            provenance_notes=f"Curated and verified records adhering to KathaYantra Publication Policy v2.0.0.",
            target_count=10,
            actual_record_count=len(eligible_records),
            total_records=len(eligible_records),
            status="curated_and_verified" if len(eligible_records) >= 10 else "partial_curation",
            validation_status="valid",
        ),
    )

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        temp_path = target_dir / f".tmp_{file_path.name}"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(envelope.model_dump_json(indent=2))
        temp_path.replace(file_path)

    return len(eligible_records), violations_log


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and publish verified KathaYantra seed datasets.")
    parser.add_argument("--country", type=str, help="Build only a specific country (e.g. IN, JP, US)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing to disk")
    parser.add_argument("--verbose", action="store_true", help="Print detailed per-record logs")
    args = parser.parse_args()

    countries_to_process = [args.country.upper()] if args.country else sorted(list(SUPPORTED_COUNTRY_CODES.keys()))

    print("=" * 80)
    print("  KATHAYANTRA — VERIFIED DATASET BUILDER & SEED POPULATOR")
    print(f"  Mode: {'DRY RUN (No files written)' if args.dry_run else 'PERSIST TO DISK'}")
    print("=" * 80)

    total_published = 0
    total_violations = 0

    for country in countries_to_process:
        if country not in SUPPORTED_COUNTRY_CODES:
            print(f"Error: Country '{country}' is not supported.")
            continue

        c_name = SUPPORTED_COUNTRY_CODES[country]
        records = get_curated_records_for_country(country)
        folklore_recs = [r for r in records if r.category == CategoryEnum.FOLKLORE]
        urban_recs = [r for r in records if r.category == CategoryEnum.URBAN_LEGEND]

        folk_count, folk_viols = build_and_publish_partition(
            country_code=country,
            category=CategoryEnum.FOLKLORE,
            records=folklore_recs,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        urban_count, urban_viols = build_and_publish_partition(
            country_code=country,
            category=CategoryEnum.URBAN_LEGEND,
            records=urban_recs,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        total_published += (folk_count + urban_count)
        total_violations += len(folk_viols) + len(urban_viols)

        status_tag = "OK" if (folk_count == 10 and urban_count == 10) else "PARTIAL"
        print(f"[{status_tag}] {country} ({c_name}): {folk_count}/10 folklore, {urban_count}/10 urban legends.")

    print("-" * 80)
    print(f"Total Eligible Stories Processed: {total_published}")
    print(f"Total Policy Violations / Rejections: {total_violations}")

    if not args.dry_run:
        manifest_path = manifest_service.save_manifest()
        print(f"Updated dataset manifest at: {manifest_path}")

    print("=" * 80)
    return 0 if total_violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
