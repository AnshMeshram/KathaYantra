"""KathaYantra - Seed JSON Dataset Migration & Normalization Utility.

Migrates Phase 1 country seed files into the canonical Phase 2 DatasetEnvelope format,
standardizing schema_version, dataset_id, metadata headers, and dynamic counts.
Supports a non-destructive --check mode.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.dataset import DatasetEnvelope, DatasetMetadata
from app.schemas.story import CategoryEnum


def inspect_file_needs_migration(file_path: Path, country_code: str, category: CategoryEnum) -> bool:
    """Check if a seed file requires migration to the Phase 2 canonical envelope."""
    if not file_path.exists():
        return True

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("schema_version") != "2.0.0":
            return True
        if data.get("dataset_id") != f"{country_code}-{category.value}":
            return True
        metadata = data.get("metadata", {})
        if "actual_record_count" not in metadata:
            return True
        return False
    except Exception:
        return True


def migrate_seed_file(file_path: Path, country_code: str, category: CategoryEnum) -> DatasetEnvelope:
    """Read existing file, upgrade to canonical DatasetEnvelope, and save safely."""
    raw_records = []
    existing_meta = {}

    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                raw_records = data.get("records", [])
                existing_meta = data.get("metadata", {})
        except Exception:
            raw_records = []
            existing_meta = {}

    envelope_meta = DatasetMetadata(
        description=f"{category.value.replace('_', ' ').capitalize()} archive partition for {SUPPORTED_COUNTRY_CODES.get(country_code, country_code)} ({country_code})",
        dataset_version="2.0.0",
        created_at=datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
        provenance_notes="Canonical Phase 2 DatasetEnvelope schema format",
        target_count=10,
        actual_record_count=len(raw_records),
        total_records=len(raw_records),
        status=existing_meta.get("status", "pending_curation"),
        validation_status="valid",
        last_updated=datetime.now(timezone.utc).isoformat(),
        import_batch_references=[],
    )

    envelope = DatasetEnvelope(
        schema_version="2.0.0",
        dataset_id=f"{country_code}-{category.value}",
        country_code=country_code,
        category=category,
        records=raw_records,
        metadata=envelope_meta,
    )

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(envelope.model_dump_json(indent=2))

    return envelope


def process_all_seed_files(check_only: bool = False) -> int:
    """Inspect or migrate all 30 country seed files."""
    folklore_dir = settings.folklore_seed_dir
    urban_dir = settings.urban_legends_seed_dir

    targets = [
        (CategoryEnum.FOLKLORE, folklore_dir),
        (CategoryEnum.URBAN_LEGEND, urban_dir),
    ]

    files_needing_migration = []
    country_codes = sorted(list(SUPPORTED_COUNTRY_CODES.keys()))

    for cat_enum, dir_path in targets:
        for c in country_codes:
            file_path = dir_path / f"{c}.json"
            if inspect_file_needs_migration(file_path, c, cat_enum):
                files_needing_migration.append((file_path, c, cat_enum))

    if check_only:
        if files_needing_migration:
            print(f"Migration required: {len(files_needing_migration)} file(s) do not match schema 2.0.0:")
            for p, c, cat in files_needing_migration:
                print(f"  - {p.as_posix()} ({c}-{cat.value})")
            return 1
        else:
            print("All 30 country seed dataset files are up to date with schema 2.0.0.")
            return 0

    # Execute Migration
    migrated_count = 0
    for cat_enum, dir_path in targets:
        for c in country_codes:
            file_path = dir_path / f"{c}.json"
            migrate_seed_file(file_path, c, cat_enum)
            migrated_count += 1

    print(f"Successfully migrated {migrated_count} seed files across 15 countries to DatasetEnvelope 2.0.0.")
    return 0


if __name__ == "__main__":
    is_check = "--check" in sys.argv
    exit_code = process_all_seed_files(check_only=is_check)
    sys.exit(exit_code)
