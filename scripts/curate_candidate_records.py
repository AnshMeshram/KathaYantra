"""CLI Curatorial Review Tool for KathaYantra Staged Import Candidates.

Usage:
    python scripts/curate_candidate_records.py --list [--country IN] [--category folklore]
    python scripts/curate_candidate_records.py --inspect CAND-IA-0001
    python scripts/curate_candidate_records.py --approve CAND-IA-0001 --curator "Editor Name" --notes "Verified against LOC"
    python scripts/curate_candidate_records.py --reject CAND-IA-0001 --curator "Editor Name" --notes "Copyrighted source"
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.import_candidate import CandidateDispositionEnum
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum
from app.services.curation_service import curation_service


def main() -> int:
    parser = argparse.ArgumentParser(description="KathaYantra Candidate Curation and Editorial Review CLI.")
    parser.add_argument("--list", action="store_true", help="List candidates in the review queue")
    parser.add_argument("--inspect", type=str, help="Inspect a specific candidate ID in detail")
    parser.add_argument("--approve", type=str, help="Candidate ID to approve for publication")
    parser.add_argument("--reject", type=str, help="Candidate ID to reject from publication")
    parser.add_argument("--curator", type=str, default="Human Curator", help="Curator identifier or name")
    parser.add_argument("--notes", type=str, default="", help="Editorial review notes")
    parser.add_argument("--country", type=str, help="Filter by proposed ISO country code")
    parser.add_argument("--category", type=str, choices=["folklore", "urban_legend"], help="Filter by category")
    parser.add_argument("--rights-status", type=str, help="Set rights status (approved, public_domain_verified, metadata_only)")

    args = parser.parse_args()

    cat_enum = CategoryEnum(args.category) if args.category else None

    if args.list:
        candidates = curation_service.get_review_queue(
            country_code=args.country,
            category=cat_enum,
        )
        print("=" * 80)
        print(f"  KATHAYANTRA — CANDIDATE REVIEW QUEUE ({len(candidates)} items)")
        print("=" * 80)
        if not candidates:
            print("No candidates currently awaiting review in this view.")
        else:
            print(f"{'Candidate ID':<16} {'Country':<8} {'Category':<14} {'Source':<16} {'Title':<30}")
            print("-" * 80)
            for c in candidates[:50]:
                cntry = c.proposed_country_code or "N/A"
                cat = c.proposed_category.value if c.proposed_category else "N/A"
                src = c.source_registry_id or "N/A"
                title = (c.raw_title[:28] + "..") if len(c.raw_title) > 30 else c.raw_title
                print(f"{c.candidate_id:<16} {cntry:<8} {cat:<14} {src:<16} {title:<30}")
            if len(candidates) > 50:
                print(f"... and {len(candidates) - 50} more candidates.")
        print("=" * 80)
        return 0

    if args.inspect:
        candidate = curation_service.get_candidate_by_id(args.inspect)
        if not candidate:
            print(f"Error: Candidate '{args.inspect}' not found.")
            return 1
        print("=" * 80)
        print(f"  CANDIDATE INSPECTION: {candidate.candidate_id}")
        print("=" * 80)
        print(f"Raw Title:       {candidate.raw_title}")
        print(f"Upstream Source: {candidate.source_registry_id} ({candidate.raw_url or 'No URL'})")
        print(f"Batch ID:        {candidate.import_batch_id}")
        print(f"Country Code:    {candidate.proposed_country_code} (Raw: {candidate.raw_nation})")
        print(f"Category:        {candidate.proposed_category}")
        print(f"Disposition:     {candidate.disposition.value}")
        print(f"Rights Status:   {candidate.rights_status.value}")
        print(f"Verification:    {candidate.verification_status.value}")
        print(f"Summary:         {candidate.proposed_summary or '(None)'}")
        print("-" * 80)
        # Run verification check
        res = curation_service.verification_service.verify_candidate(candidate)
        print(f"Verification Pass: {'YES' if res.is_verified else 'NO'}")
        if res.findings:
            print("Findings:")
            for f in res.findings:
                print(f"  - {f}")
        print("=" * 80)
        return 0

    if args.approve:
        rights_enum = RightsStatusEnum(args.rights_status) if args.rights_status else RightsStatusEnum.APPROVED
        res = curation_service.review_candidate(
            candidate_id=args.approve,
            curator=args.curator,
            approved=True,
            notes=args.notes or "Approved via CLI curation tool",
            rights_status=rights_enum,
        )
        if not res:
            print(f"Error: Candidate '{args.approve}' not found.")
            return 1
        print(f"Successfully approved candidate '{args.approve}'. Disposition: {res.disposition.value}")
        return 0

    if args.reject:
        res = curation_service.review_candidate(
            candidate_id=args.reject,
            curator=args.curator,
            approved=False,
            notes=args.notes or "Rejected via CLI curation tool",
        )
        if not res:
            print(f"Error: Candidate '{args.reject}' not found.")
            return 1
        print(f"Successfully rejected candidate '{args.reject}'. Disposition: {res.disposition.value}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
