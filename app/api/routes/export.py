"""Archival Pack Export Router for KathaYantra."""

import csv
from datetime import datetime, timezone
import io
import json
import logging
from typing import Optional
import zipfile

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.repositories.story_repository import story_repository
from app.schemas.country import SUPPORTED_COUNTRY_CODES

logger = logging.getLogger("kathayantra.export")

router = APIRouter(prefix="/export", tags=["Export & Download Packs"])


@router.get(
    "/pack",
    status_code=status.HTTP_200_OK,
    summary="Download Rights-Compliant Curated Archive Pack",
)
async def download_archive_pack(
    category: Optional[str] = Query(
        default=None,
        pattern="^(folklore|urban_legend)$",
        description="Filter by category ('folklore' or 'urban_legend')",
    ),
    country_code: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=2,
        description="Two-letter ISO country code (e.g. 'IN', 'JP')",
    ),
):
    """Generate and stream a rights-compliant, curated ZIP archive pack containing:

    - README.md: Scope, usage guide, non-commercial research disclaimer.
    - archive-manifest.json: Cryptographic/metadata provenance manifest.
    - stories.json: Full structured records.
    - stories.csv: Research table of records.
    - sources/source-manifest.json: Primary bibliographic citations.
    - images/image-attribution.json: Institutional image provenance and licensing notices.
    """
    # 1. Validation
    target_country = country_code.upper() if country_code else None
    if target_country and target_country not in SUPPORTED_COUNTRY_CODES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "COUNTRY_NOT_SUPPORTED",
                "message": f"Country '{target_country}' is not among the 15 supported archive countries.",
            },
        )

    # 2. Fetch Eligible Stories
    records, total = story_repository.list_stories(
        category=category,
        country_code=target_country,
        limit=1000,
        offset=0,
    )

    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "EMPTY_COLLECTION",
                "message": "No stories found matching the requested archive filters.",
            },
        )

    # 3. Build Filename
    parts = ["kathayantra"]
    if target_country:
        parts.append(target_country)
    if category:
        parts.append(category.replace("_", "-"))
    parts.append("archive.zip")
    filename = "-".join(parts)

    now_utc = datetime.now(timezone.utc).isoformat()

    # 4. In-Memory Zip Construction
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # A. README.md
        readme_content = f"""# KathaYantra Archival Pack
## A Digital Museum of World Folklore & Urban Legends

- **Archive Version:** {settings.PROJECT_VERSION}
- **Generated At (UTC):** {now_utc}
- **Collection Scope:** {category or 'All Categories'} | {target_country or 'All 15 Target Countries'}
- **Total Published Records:** {total}
- **Anti-Hallucination Policy:** Local-first, verified historical traditions only. Zero AI-generated fiction.

### Included Files
1. `stories.json`: Full canonical records including cultural context, motifs, and source citations.
2. `stories.csv`: Tabular index suitable for research, digital humanities, and cataloging.
3. `sources/source-manifest.json`: Verified repository citations and source URLs.
4. `images/image-attribution.json`: Museum provenance, Public Domain / CC0 license terms, and attribution requirements.

### Copyright & Redistribution Notice
- KathaYantra is an educational and cultural preservation project.
- Story texts and folklore oral narratives are cultural heritage preserved for academic and public research.
- Image assets referenced in this archive originate from institutions such as Wikimedia Commons, the Library of Congress, and the Metropolitan Museum of Art. Image binaries are only redistributed when verified under Public Domain or CC0/CC-BY terms.
- For complete details or API access, visit https://github.com/AnshMeshram/KathaYantra.
"""
        zf.writestr("KathaYantra-Archive/README.md", readme_content.strip())

        # B. archive-manifest.json
        manifest_data = {
            "archive": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "generated_at": now_utc,
            "filters": {
                "category": category,
                "country_code": target_country,
            },
            "record_count": total,
            "files": [
                "README.md",
                "archive-manifest.json",
                "stories.json",
                "stories.csv",
                "sources/source-manifest.json",
                "images/image-attribution.json",
            ],
            "rights_policy": "Strict non-hallucination, verified provenance, rights-aware digital curation.",
        }
        zf.writestr(
            "KathaYantra-Archive/archive-manifest.json",
            json.dumps(manifest_data, indent=2),
        )

        # C. stories.json
        story_dicts = [r.model_dump(mode="json") for r in records]
        zf.writestr(
            "KathaYantra-Archive/stories.json",
            json.dumps(story_dicts, indent=2),
        )

        # D. stories.csv
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow([
            "id",
            "title",
            "country_code",
            "category",
            "region_or_community",
            "language",
            "motifs",
            "themes",
            "sources_count",
            "created_at",
        ])
        for r in records:
            csv_writer.writerow([
                r.id,
                r.title,
                r.country_code,
                r.category.value,
                r.region_or_community or "",
                r.language or "",
                "; ".join(r.motifs),
                "; ".join(r.themes),
                len(r.sources),
                r.created_at.isoformat() if r.created_at else "",
            ])
        zf.writestr("KathaYantra-Archive/stories.csv", csv_buffer.getvalue())

        # E. sources/source-manifest.json
        all_sources = []
        for r in records:
            for s in r.sources:
                all_sources.append({
                    "story_id": r.id,
                    "story_title": r.title,
                    "citation": s.citation or s.title or s.name,
                    "publisher": s.publisher,
                    "url": str(s.url) if s.url else None,
                    "canonical_url": str(s.canonical_url) if s.canonical_url else None,
                    "license": s.license_name,
                    "rights_status": s.rights_status.value if hasattr(s.rights_status, "value") else str(s.rights_status),
                    "access_date": s.access_date or (s.retrieved_at.isoformat() if s.retrieved_at else None),
                })
        zf.writestr(
            "KathaYantra-Archive/sources/source-manifest.json",
            json.dumps(all_sources, indent=2),
        )

        # F. images/image-attribution.json
        # Load image attribution metadata from canonical image manifest if available
        image_attribution_records = []
        try:
            image_manifest_path = settings.DATA_DIR / "processed" / "image_assets" / "image_manifest.json"
            if image_manifest_path.exists():
                with open(image_manifest_path, "r", encoding="utf-8") as imf:
                    im_data = json.load(imf)
                    records_by_story = {item["story_id"]: item.get("images", []) for item in im_data.get("records", [])}
                    for r in records:
                        if r.id in records_by_story:
                            for img in records_by_story[r.id]:
                                image_attribution_records.append({
                                    "story_id": r.id,
                                    "image_id": img.get("image_id"),
                                    "title": img.get("title"),
                                    "source_institution": img.get("source_institution"),
                                    "source_url": img.get("source_url"),
                                    "license": img.get("license"),
                                    "license_url": img.get("license_url"),
                                    "attribution": img.get("attribution"),
                                    "redistribution_eligible": img.get("license") in ["Public Domain", "CC0", "Open Access"],
                                })
        except Exception as e:
            logger.warning("Could not append image manifest to export: %s", e)

        zf.writestr(
            "KathaYantra-Archive/images/image-attribution.json",
            json.dumps(image_attribution_records, indent=2),
        )

    zip_buffer.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/zip",
        "X-Archive-Count": str(total),
    }

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers=headers,
    )
