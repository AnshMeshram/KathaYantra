"""Wikimedia / Wikipedia REST API Connector for KathaYantra."""

import re
from typing import Any, Optional
from urllib.parse import quote
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class MediaWikiConnector(BaseConnector):
    """Connector for the official Wikimedia / Wikipedia REST API."""

    def __init__(
        self,
        source_id: str = "wikimedia_wikipedia_api",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
        base_url: str = "https://en.wikipedia.org",
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()
        self.base_url = base_url.rstrip("/")

    async def check_health(self) -> dict[str, Any]:
        """Verify Wikimedia REST API availability."""
        url = f"{self.base_url}/w/rest.php/v1/search/page"
        try:
            data = await self.http_client.get_json(
                url,
                params={"q": "Folklore", "limit": 1},
                source_id=self.source_id,
                use_cache=True,
                ttl_seconds=300,
            )
            if isinstance(data, dict) and "pages" in data:
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Wikimedia REST API is reachable and responsive",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "API response missing expected 'pages' field",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Connection error: {exc}",
            }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Wikipedia pages and convert them into ImportCandidates."""
        search_url = f"{self.base_url}/w/rest.php/v1/search/page"
        params = {"q": query, "limit": min(limit, 50)}

        data = await self.http_client.get_json(
            search_url,
            params=params,
            source_id=self.source_id,
        )

        if not isinstance(data, dict) or "pages" not in data:
            raise PayloadValidationError("Missing 'pages' list in Wikimedia response", source_id=self.source_id)

        if not data["pages"]:
            return []

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-wikimedia-default")

        for item in data["pages"]:
            try:
                candidate = self.normalize_record(
                    item,
                    batch_id=batch_id,
                    proposed_country_code=country_code,
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception as exc:
                # Log and skip invalid record rather than breaking entire batch
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Fetch summary for a specific Wikipedia page title or key."""
        encoded_title = quote(external_id)
        summary_url = f"{self.base_url}/api/rest_v1/page/summary/{encoded_title}"
        try:
            item = await self.http_client.get_json(summary_url, source_id=self.source_id)
            if not isinstance(item, dict):
                return None
            return self.normalize_record(item, batch_id="batch-single-lookup")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a Wikimedia page object into a validated ImportCandidate."""
        page_id = raw_item.get("id") or raw_item.get("pageid")
        title = raw_item.get("title") or raw_item.get("key") or "Untitled"

        # Canonical URL construction
        canonical_url = None
        content_urls = raw_item.get("content_urls")
        if isinstance(content_urls, dict) and "desktop" in content_urls:
            canonical_url = content_urls["desktop"].get("page")
        if not canonical_url:
            key_name = raw_item.get("key") or title.replace(" ", "_")
            canonical_url = f"{self.base_url}/wiki/{key_name}"

        # Summary / excerpt extraction (strip HTML tags)
        excerpt = raw_item.get("excerpt") or raw_item.get("extract") or raw_item.get("description") or ""
        clean_excerpt = re.sub(r"<[^>]+>", "", excerpt).strip()
        proposed_summary = clean_excerpt[:500] if clean_excerpt else f"Article discussing {title} on Wikipedia."

        ext_id = str(page_id) if page_id else (raw_item.get("key") or title)
        candidate_id = f"CAND-WIKI-{ext_id}"

        review_notes = (
            "Content derived from Wikipedia. Subject to CC BY-SA 4.0; attribution and share-alike required if text is adapted."
        )

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=ext_id,
            raw_title=title,
            raw_language="en",
            raw_url=canonical_url,
            raw_metadata={
                "page_id": page_id,
                "key": raw_item.get("key"),
                "description": raw_item.get("description"),
                "thumbnail": raw_item.get("thumbnail"),
                "license": "CC-BY-SA-4.0",
                "project": "en.wikipedia.org",
            },
            raw_text_available=False,
            rights_status=RightsStatusEnum.METADATA_ONLY,
            proposed_country_code=proposed_country_code,
            proposed_category=proposed_category,
            proposed_summary=proposed_summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
