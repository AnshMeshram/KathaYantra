"""Curation Status and Candidate Review Audit Reporting CLI for KathaYantra.

Generates comprehensive reports on candidate intake, review dispositions,
rights clearance status, and curatorial throughput.

Usage:
    python scripts/report_curation_status.py [--markdown] [--json] [--output report.md]
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.repositories.candidate_repository import candidate_repository
from app.services.coverage_planner import coverage_planner
from app.services.manifest_service import manifest_service


def generate_curation_report() -> dict:
    """Compile candidate metrics and published verification metrics."""
    candidates = candidate_repository.load_all_candidates()
    batches = candidate_repository.list_all_batches()
    manifest = manifest_service.compute_manifest()

    disposition_counts = Counter(c.disposition.value for c in candidates)
    candidate_rights_counts = Counter(c.rights_status.value for c in candidates)
    country_counts = Counter(c.proposed_country_code for c in candidates if c.proposed_country_code)

    approved_count = disposition_counts.get("approved_for_publication", 0)
    rejected_count = disposition_counts.get("rejected", 0)
    reviewed_total = sum(1 for c in candidates if c.reviewed_by is not None)

    return {
        "report_generated_at": datetime.now(timezone.utc).isoformat(),
        "total_batches_ingested": len(batches),
        "total_staged_candidates": len(candidates),
        "disposition_breakdown": dict(disposition_counts),
        "candidate_rights_breakdown": dict(candidate_rights_counts),
        "candidates_by_proposed_country": dict(country_counts),
        "curation_throughput": {
            "total_candidates_reviewed": reviewed_total,
            "approved_for_publication": approved_count,
            "rejected_from_publication": rejected_count,
            "pending_editorial_review": len(candidates) - reviewed_total,
        },
        "published_archive_metrics": {
            "total_published_records": manifest.actual_record_count,
            "published_folklore": manifest.current_actual_counts.folklore_records,
            "published_urban_legends": manifest.current_actual_counts.urban_legend_records,
            "published_verified_records": manifest.published_and_verified_records,
            "records_by_rights_status": {
                "approved": manifest.published_and_verified_records,
                "metadata_only": manifest.metadata_only_records,
                "needs_rights_review": manifest.rights_pending_records,
            },
        },
    }


def format_markdown(data: dict) -> str:
    lines = [
        "# KathaYantra — Curation Status and Editorial Review Audit Report",
        "",
        f"**Generated:** `{data['report_generated_at']}`  ",
        f"**Total Import Batches:** {data['total_batches_ingested']}  ",
        f"**Total Staged Candidates:** {data['total_staged_candidates']}  ",
        f"**Published Story Records:** {data['published_archive_metrics']['total_published_records']}  ",
        "",
        "---",
        "",
        "## 1. Candidate Dispositions",
        "",
        "| Disposition Stage | Count | Description |",
        "|:---|:---:|:---|",
    ]

    for disp, cnt in sorted(data["disposition_breakdown"].items()):
        lines.append(f"| `{disp}` | {cnt} | Staged candidate state |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Curation Throughput & Review Decisions",
        "",
        f"- **Candidates Reviewed:** {data['curation_throughput']['total_candidates_reviewed']}",
        f"- **Approved for Publication:** {data['curation_throughput']['approved_for_publication']}",
        f"- **Rejected from Publication:** {data['curation_throughput']['rejected_from_publication']}",
        f"- **Pending Editorial Action:** {data['curation_throughput']['pending_editorial_review']}",
        "",
        "---",
        "",
        "## 3. Published Archive Status",
        "",
        f"- **Total Published Records:** {data['published_archive_metrics']['total_published_records']}",
        f"- **Folklore Records:** {data['published_archive_metrics']['published_folklore']}",
        f"- **Urban Legends:** {data['published_archive_metrics']['published_urban_legends']}",
        f"- **Verified Records:** {data['published_archive_metrics']['published_verified_records']}",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate KathaYantra Curation Status Report.")
    parser.add_argument("--markdown", action="store_true", help="Format output as Markdown")
    parser.add_argument("--json", action="store_true", help="Format output as JSON")
    parser.add_argument("--output", type=str, help="Save report to file")
    args = parser.parse_args()

    report_data = generate_curation_report()

    if args.json:
        output_text = json.dumps(report_data, indent=2)
    else:
        output_text = format_markdown(report_data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"Curation report saved to: {out_path}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
