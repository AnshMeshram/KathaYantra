"""CLI Utility to Inspect Country Quotas and Deficits for KathaYantra Archive.

Usage:
    python scripts/check_country_quotas.py [--markdown] [--json] [--quiet]
"""

import argparse
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.coverage_planner import coverage_planner


def main() -> int:
    parser = argparse.ArgumentParser(description="Check KathaYantra Country Story Quotas and Archive Deficits.")
    parser.add_argument("--markdown", action="store_true", help="Print report formatted as Markdown")
    parser.add_argument("--json", action="store_true", help="Print report as JSON")
    parser.add_argument("--quiet", action="store_true", help="Minimal output, returns exit code equal to remaining deficit")
    args = parser.parse_args()

    report = coverage_planner.compile_coverage_report()

    if args.json:
        print(report.model_dump_json(indent=2))
        return 0 if report.total_deficit == 0 else 1

    if args.markdown:
        print(coverage_planner.generate_markdown_report())
        return 0 if report.total_deficit == 0 else 1

    if args.quiet:
        print(f"Verified Records: {report.actual_total_records}/{report.required_total_records} (Deficit: {report.total_deficit})")
        return 0 if report.total_deficit == 0 else 1

    print("=" * 80)
    print("  KATHAYANTRA — WORLD FOLKLORE & URBAN LEGEND QUOTA TRACKER")
    print("=" * 80)
    print(f"Archive Completion: {report.actual_total_records} / {report.required_total_records} ({report.completion_percentage}%)")
    print(f"Partitions Met:     {report.partitions_met} / {report.total_partitions} partitions")
    print(f"Countries Complete: {report.countries_fully_met} / {report.target_countries} countries")
    print(f"Remaining Deficit:  {report.total_deficit} stories")
    print("-" * 80)
    print(f"{'Code':<6} {'Country':<18} {'Folklore (Act/Tgt)':<20} {'Urban Legends (Act/Tgt)':<24} {'Status':<8}")
    print("-" * 80)

    for code, c_summary in sorted(report.countries.items()):
        folk_str = f"{c_summary.folklore.actual} / {c_summary.folklore.target}"
        urban_str = f"{c_summary.urban_legend.actual} / {c_summary.urban_legend.target}"
        status_str = "MET" if c_summary.is_complete else f"DEFICIT ({c_summary.total_deficit})"
        print(f"{code:<6} {c_summary.country_name:<18} {folk_str:<20} {urban_str:<24} {status_str:<8}")

    print("=" * 80)
    return 0 if report.total_deficit == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
