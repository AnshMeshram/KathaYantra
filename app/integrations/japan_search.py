"""Japan Search Cultural Heritage API Connector for KathaYantra."""

from typing import Any, Optional
from app.core.config import settings
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class JapanSearchConnector(BaseConnector):
    """Connector for the National Diet Library's Japan Search (JPS) Cultural Heritage Platform."""

    SEARCH_ENDPOINT = "https://jpsearch.go.jp/api/item/search"
    BASE_URL = "https://jpsearch.go.jp"

    def __init__(
        self,
        source_id: str = "japan_search",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
        api_key: Optional[str] = None,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()
        self.api_key = api_key if api_key is not None else settings.JAPAN_SEARCH_API_KEY

    async def check_health(self) -> dict[str, Any]:
        """Verify Japan Search API reachability."""
        params = {"keyword": "妖怪", "size": 1}
        try:
            data = await self.http_client.get_json(self.SEARCH_ENDPOINT, params=params, source_id=self.source_id)
            if isinstance(data, dict) and "items" in data:
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Japan Search REST API is operational",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "Japan Search responded without expected 'items' key",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Japan Search unreachable: {exc}",
            }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = "JP",
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Japan Search for folklore and mythical cultural items."""
        bounded_limit = min(limit, 50)
        params = {
            "keyword": query,
            "size": bounded_limit,
        }

        data = await self.http_client.get_json(self.SEARCH_ENDPOINT, params=params, source_id=self.source_id)
        if not isinstance(data, dict) or "items" not in data:
            raise PayloadValidationError("Invalid response structure from Japan Search", source_id=self.source_id)

        items = data.get("items", [])
        if not items:
            return []

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-jps-default")

        for item in data.get("items", []):
            try:
                candidate = self.normalize_record(
                    item,
                    batch_id=batch_id,
                    proposed_country_code=country_code or "JP",
                    proposed_category=category or CategoryEnum.FOLKLORE,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Retrieve item details from Japan Search by item ID."""
        clean_id = external_id.strip()
        url = f"{self.BASE_URL}/item/{clean_id}.json"
        try:
            data = await self.http_client.get_json(url, source_id=self.source_id)
            if not isinstance(data, dict):
                return None
            return self.normalize_record(data, batch_id="batch-jps-single")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = "JP",
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a Japan Search JSON record into an ImportCandidate."""
        item_id = raw_item.get("id") or raw_item.get("jps_id") or ""
        clean_ext_id = str(item_id).replace("/", "_").strip("_")
        candidate_id = f"CAND-JPS-{clean_ext_id}"

        title = raw_item.get("title") or raw_item.get("name") or "Untitled JPS Item"
        if isinstance(title, list) and title:
            title = str(title[0])

        canonical_url = raw_item.get("link") or f"{self.BASE_URL}/item/{item_id}"

        description = raw_item.get("description") or raw_item.get("contents") or ""
        if isinstance(description, list) and description:
            description = " ".join(str(d) for d in description)
        summary = str(description)[:500] if description else f"Japanese cultural heritage entity: {title}"

        review_notes = f"Japan Search cultural database record ({item_id}). Metadata-only ingestion; full text not harvested."

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=str(item_id),
            raw_title=str(title),
            raw_language="ja",
            raw_url=canonical_url,
            raw_metadata={
                "jps_id": item_id,
                "database": raw_item.get("database"),
                "provider": raw_item.get("provider"),
                "license": raw_item.get("license"),
            },
            raw_text_available=False,
            rights_status=RightsStatusEnum.METADATA_ONLY,
            proposed_country_code="JP",
            proposed_category=proposed_category or CategoryEnum.FOLKLORE,
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
