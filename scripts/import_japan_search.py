#!/usr/bin/env python3
"""CLI Tool to import Japanese folklore and supernatural items from Japan Search."""

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
        description="Import Japanese cultural folklore items from Japan Search Platform."
    )
    parser.add_argument("--query", "-q", default="妖怪", help="Search keyword (kanji or English)")
    parser.add_argument(
        "--category",
        choices=["folklore", "urban_legend"],
        default="folklore",
        help="Target category",
    )
    parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum items to retrieve")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without persisting candidates")

    args = parser.parse_args()

    cat_enum = CategoryEnum(args.category) if args.category else None

    print(f"=== Importing Japan Search items for '{args.query}' ===")
    if args.dry_run:
        print("[DRY RUN MODE: Candidates will NOT be written to disk]")

    manifest = asyncio.run(
        import_pipeline.run_import_batch(
            source_id="japan_search",
            query=args.query,
            country_code="JP",
            category=cat_enum,
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
