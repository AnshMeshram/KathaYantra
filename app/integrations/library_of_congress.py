"""Library of Congress JSON API Connector for KathaYantra."""

import re
from typing import Any, Optional
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class LibraryOfCongressConnector(BaseConnector):
    """Connector for the official Library of Congress JSON and YAML Search API."""

    BASE_URL = "https://www.loc.gov"

    def __init__(
        self,
        source_id: str = "library_of_congress_api",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()

    async def check_health(self) -> dict[str, Any]:
        """Verify Library of Congress API endpoint availability."""
        url = f"{self.BASE_URL}/search/"
        params = {"q": "folklore", "fo": "json", "c": 1}
        try:
            data = await self.http_client.get_json(
                url,
                params=params,
                source_id=self.source_id,
                ttl_seconds=300,
            )
            if isinstance(data, dict) and "results" in data:
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Library of Congress API is operational",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "LOC response missing 'results' array",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"LOC API unreachable: {exc}",
            }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Library of Congress collections and normalize into ImportCandidates."""
        url = f"{self.BASE_URL}/search/"
        bounded_limit = min(limit, 50)
        params = {
            "q": query,
            "fo": "json",
            "c": bounded_limit,
        }

        data = await self.http_client.get_json(url, params=params, source_id=self.source_id)
        if not isinstance(data, dict) or "results" not in data:
            raise PayloadValidationError("Missing 'results' in LOC response", source_id=self.source_id)

        if not data["results"]:
            return []

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-loc-default")

        for item in data["results"]:
            try:
                candidate = self.normalize_record(
                    item,
                    batch_id=batch_id,
                    proposed_country_code=country_code or "US",
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Fetch item record details by LOC identifier."""
        clean_id = external_id.strip("/").split("/")[-1]
        url = f"{self.BASE_URL}/item/{clean_id}/"
        params = {"fo": "json"}
        try:
            data = await self.http_client.get_json(url, params=params, source_id=self.source_id)
            if not isinstance(data, dict) or "item" not in data:
                return None
            return self.normalize_record(data["item"], batch_id="batch-loc-single")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a Library of Congress item dictionary into an ImportCandidate."""
        title = raw_item.get("title") or "Untitled LOC Record"
        if isinstance(title, list) and title:
            title = str(title[0])

        item_url = raw_item.get("url") or raw_item.get("id") or ""
        ext_id = raw_item.get("number_lccn") or raw_item.get("id") or item_url
        if isinstance(ext_id, list) and ext_id:
            ext_id = ext_id[0]
        ext_id = str(ext_id).strip("/").split("/")[-1]

        candidate_id = f"CAND-LOC-{ext_id}"

        # Description / Summary extraction
        description_field = raw_item.get("description") or raw_item.get("summary") or ""
        if isinstance(description_field, list) and description_field:
            description_field = " ".join(str(d) for d in description_field)
        summary = str(description_field)[:500] if description_field else f"Library of Congress collection item: {title}"

        # Rights / Public domain heuristic
        date_str = raw_item.get("date") or ""
        is_pre_1929 = False
        years = re.findall(r"\b(1[789][0-9]{2}|19[012][0-9])\b", str(date_str))
        if years and int(years[0]) <= 1928:
            is_pre_1929 = True

        rights_notes = raw_item.get("rights") or []
        rights_str = " ".join(rights_notes) if isinstance(rights_notes, list) else str(rights_notes)

        if is_pre_1929 or "no known restrictions" in rights_str.lower():
            rights_status = RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
        else:
            rights_status = RightsStatusEnum.METADATA_ONLY

        review_notes = f"Library of Congress bibliographic record. Date: {date_str}. Rights info: {rights_str[:150]}"

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=ext_id,
            raw_title=title,
            raw_language="en",
            raw_url=item_url if item_url.startswith("http") else f"{self.BASE_URL}{item_url}",
            raw_metadata={
                "contributors": raw_item.get("contributors"),
                "date": date_str,
                "original_format": raw_item.get("original_format"),
                "rights": rights_notes,
                "subject": raw_item.get("subject"),
            },
            raw_text_available=False,
            rights_status=rights_status,
            proposed_country_code=proposed_country_code or "US",
            proposed_category=proposed_category,
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
