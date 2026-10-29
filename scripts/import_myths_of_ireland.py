#!/usr/bin/env python3
"""CLI Tool to import Irish folklore candidates from the Myths of Ireland CC BY 4.0 structured dataset."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.story import CategoryEnum
from app.services.import_pipeline import import_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import Irish folklore candidates from Myths of Ireland open dataset (CC BY 4.0)."
    )
    parser.add_argument("--query", "-q", default="all", help="Keyword filter or 'all' to import entire index")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Maximum stories to stage")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without persisting candidates")

    args = parser.parse_args()

    print(f"=== Importing Myths of Ireland entries (query: '{args.query}') ===")
    if args.dry_run:
        print("[DRY RUN MODE: Candidates will NOT be written to disk]")

    manifest = asyncio.run(
        import_pipeline.run_import_batch(
            source_id="myths_of_ireland",
            query=args.query,
            country_code="IE",
            category=CategoryEnum.FOLKLORE,
            limit=args.limit,
            dry_run=args.dry_run,
        )
    )

    print("-" * 50)
    print(f"Batch ID:        {manifest.batch_id}")
    print(f"Retrieved:       {manifest.retrieved_count}")
    print(f"Accepted:        {manifest.accepted_count}")
    print(f"Duplicates:      {manifest.duplicate_count}")
    print(f"Rights Pending:  {manifest.rights_pending_count}")
    print(f"Mapping Review:  {manifest.mapping_review_count}")
    if manifest.output_file:
        print(f"Output File:     data/processed/candidates/{manifest.output_file}")
    if manifest.errors:
        print(f"Errors ({len(manifest.errors)}): {manifest.errors}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
