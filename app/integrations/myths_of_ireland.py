"""Myths of Ireland Structured Open Dataset Connector for KathaYantra."""

import csv
import io
import json
from pathlib import Path
from typing import Any, Optional
from app.core.config import settings
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class MythsOfIrelandConnector(BaseConnector):
    """Connector for the Myths of Ireland CC BY 4.0 structured dataset."""

    DATASET_URL = "https://www.mythsofireland.com/dataset/myths_of_ireland_dataset.json"
    SOURCE_WEBSITE = "https://www.mythsofireland.com"

    def __init__(
        self,
        source_id: str = "myths_of_ireland",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
        local_cache_path: Optional[Path] = None,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()
        self.local_cache_path = local_cache_path or (settings.DATA_DIR / "cache" / "myths_of_ireland.json")

    async def check_health(self) -> dict[str, Any]:
        """Verify accessibility of the Myths of Ireland dataset."""
        if self.local_cache_path.exists():
            return {
                "source_id": self.source_id,
                "status": "ok",
                "message": f"Cached dataset available locally at {self.local_cache_path.name}",
            }
        try:
            # Check upstream availability
            data = await self.http_client.get_json(
                self.DATASET_URL,
                source_id=self.source_id,
                ttl_seconds=86400,
            )
            if isinstance(data, (list, dict)):
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Myths of Ireland dataset endpoint reachable and responsive",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "Upstream response format unexpected",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Dataset endpoint unreachable: {exc}",
            }

    async def load_raw_dataset(self) -> list[dict[str, Any]]:
        """Load dataset from local cache if present, otherwise fetch upstream and cache."""
        if self.local_cache_path.exists():
            with open(self.local_cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get("items", [])

        # Fetch upstream
        data = await self.http_client.get_json(self.DATASET_URL, source_id=self.source_id)
        items = data if isinstance(data, list) else data.get("items", [])

        # Cache locally
        self.local_cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.local_cache_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        return items

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search the dataset for matching items and normalize into ImportCandidates."""
        items = kwargs.get("preloaded_items")
        if items is None:
            try:
                items = await self.load_raw_dataset()
            except Exception:
                items = []

        q_lower = query.lower()
        matched = []
        for item in items:
            title = str(item.get("title", "")).lower()
            desc = str(item.get("summary", "") or item.get("description", "")).lower()
            if q_lower in title or q_lower in desc:
                matched.append(item)
            if len(matched) >= limit:
                break

        # If query is empty or "all", take up to limit
        if not matched and (q_lower in ("all", "*", "") or "ireland" in q_lower or "irish" in q_lower):
            matched = items[:limit]

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-moi-default")

        for item in matched:
            try:
                cand = self.normalize_record(
                    item,
                    batch_id=batch_id,
                    proposed_country_code=country_code or "IE",
                    proposed_category=category or CategoryEnum.FOLKLORE,
                )
                candidates.append(cand)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Find an item in the dataset by its slug or external id."""
        try:
            items = await self.load_raw_dataset()
            for item in items:
                if str(item.get("id")) == external_id or str(item.get("slug")) == external_id:
                    return self.normalize_record(item, batch_id="batch-moi-single")
        except Exception:
            pass
        return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a Myths of Ireland item into a validated ImportCandidate."""
        slug = raw_item.get("slug") or raw_item.get("id") or "item"
        title = raw_item.get("title") or "Untitled Irish Narrative"
        item_type = str(raw_item.get("type", "story")).lower()  # story, being, place

        url = raw_item.get("url")
        if not url:
            url = f"{self.SOURCE_WEBSITE}/stories/{slug}"

        candidate_id = f"CAND-MOI-{slug}"
        summary = raw_item.get("summary") or raw_item.get("description") or f"Traditional Irish folklore: {title}"

        review_notes = (
            f"Myths of Ireland open dataset. Entity type: {item_type}. "
            "Data licensed under CC BY 4.0. Mandatory attribution required: 'Source: Myths of Ireland (CC BY 4.0)'."
        )

        # Distinguish beings/places from stories
        disposition = CandidateDispositionEnum.NEW_CANDIDATE
        if item_type in ("being", "character", "entity", "creature"):
            review_notes += " Note: This entry describes a supernatural being/character, not an entire traditional narrative."
        elif item_type in ("place", "site", "location"):
            review_notes += " Note: This entry describes a sacred/legendary place, not an entire traditional narrative."

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=str(slug),
            raw_title=title,
            raw_language="en",
            raw_url=url,
            raw_metadata={
                "type": item_type,
                "cycle": raw_item.get("cycle"),  # Mythological, Ulster, Fenian, Historical
                "motifs": raw_item.get("motifs"),
                "license": "CC-BY-4.0",
                "attribution": "Source: Myths of Ireland (CC BY 4.0)",
            },
            raw_text_available=False,
            rights_status=RightsStatusEnum.APPROVED,  # CC BY 4.0
            proposed_country_code="IE",
            proposed_category=CategoryEnum.FOLKLORE,
            proposed_summary=summary[:500],
            disposition=disposition,
            review_notes=review_notes,
        )
