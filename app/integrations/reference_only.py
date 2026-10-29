"""Reference-Only Source Adapter for KathaYantra Archives and Catalogues.

Safely models authoritative discovery sources that lack documented public bulk APIs
(e.g. Urban Legends Online, NCAA India, Nichibunken, Dúchas, CNFCP Brazil).
Prohibits bulk scraping and ensures all ingested items remain metadata-only citations.
"""

from typing import Any, Optional
from app.integrations.base import BaseConnector
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class ReferenceOnlyConnector(BaseConnector):
    """Adapter for research references and discovery archives lacking automated bulk APIs."""

    def __init__(
        self,
        source_id: str,
        registry_item: Optional[SourceRegistryItem] = None,
        reason: Optional[str] = None,
    ):
        super().__init__(source_id, registry_item)
        self.reason = reason or (
            "Source is cataloged as a research and discovery reference. "
            "No public bulk API exists; automated scraping is strictly prohibited."
        )

    async def check_health(self) -> dict[str, Any]:
        """Verify reference source status without attempting automated network harvesting."""
        return {
            "source_id": self.source_id,
            "status": "reference_only",
            "message": self.reason,
            "canonical_url": self.registry_item.canonical_url if self.registry_item else None,
            "auth_required": False,
            "bulk_api_supported": False,
        }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Returns manually provided or curated references; refuses to perform bulk web scraping."""
        manual_records = kwargs.get("manual_records", [])
        if not manual_records:
            # Cleanly return empty list with warning note
            return []

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-ref-manual")
        for rec in manual_records[:limit]:
            try:
                candidate = self.normalize_record(
                    rec,
                    batch_id=batch_id,
                    proposed_country_code=country_code,
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Reference-only sources do not support single-ID network retrieval without manual input."""
        return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a curated bibliographic entry into a metadata-only ImportCandidate."""
        slug = raw_item.get("slug") or raw_item.get("id") or "ref"
        title = raw_item.get("title") or "Untitled Reference"
        canonical_url = raw_item.get("canonical_url") or raw_item.get("url")

        candidate_id = f"CAND-REF-{self.source_id}-{slug}"
        summary = raw_item.get("summary") or f"Curated discovery reference: {title}"

        review_notes = (
            f"Curated reference from {self.registry_item.name if self.registry_item else self.source_id}. "
            "Full text is NOT scraped or redistributed. Bibliographic citation and metadata only."
        )

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=str(slug),
            raw_title=title,
            raw_language=raw_item.get("language", "en"),
            raw_url=canonical_url,
            raw_metadata={
                "source_type": "discovery_reference",
                "notes": raw_item.get("notes"),
                "retain_metadata_only": True,
            },
            raw_text_available=False,
            rights_status=RightsStatusEnum.METADATA_ONLY,
            proposed_country_code=proposed_country_code or raw_item.get("country_code"),
            proposed_category=proposed_category or raw_item.get("category"),
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
