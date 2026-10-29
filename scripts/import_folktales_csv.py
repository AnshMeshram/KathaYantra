#!/usr/bin/env python3
"""CLI Tool to import candidate metadata from the quarantined folk_tales_deduplicated.csv."""

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
        description="Audit and stage candidates from raw folk_tales_deduplicated.csv without publishing copyrighted text."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="data/raw/folk_tales_deduplicated.csv",
        help="Path to raw CSV file (default: data/raw/folk_tales_deduplicated.csv)",
    )
    parser.add_argument("--query", "-q", default="", help="Optional keyword or title filter")
    parser.add_argument("--country", "-c", help="Target country code filter (e.g. IN, JP, IE)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Maximum candidates to stage (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without persisting candidates")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Raw CSV file not found at {input_path}")
        return 1

    print(f"=== Auditing & Staging Candidates from {input_path} ===")
    if args.dry_run:
        print("[DRY RUN MODE: Candidates will NOT be written to disk]")

    manifest = asyncio.run(
        import_pipeline.run_import_batch(
            source_id="fairytalez_raw_corpus",
            query=args.query,
            country_code=args.country,
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
