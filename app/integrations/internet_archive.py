"""Internet Archive Advanced Search and Metadata Connector for KathaYantra."""

import re
from typing import Any, Optional
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class InternetArchiveConnector(BaseConnector):
    """Connector for the Internet Archive Advanced Search API and Metadata API."""

    SEARCH_ENDPOINT = "https://archive.org/advancedsearch.php"
    METADATA_ENDPOINT = "https://archive.org/metadata"
    BASE_DETAILS_URL = "https://archive.org/details"

    def __init__(
        self,
        source_id: str = "internet_archive",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()

    async def check_health(self) -> dict[str, Any]:
        """Verify Internet Archive Advanced Search endpoint connectivity."""
        params = {
            "q": "mediatype:texts AND folklore",
            "fl[]": "identifier,title",
            "rows": 1,
            "output": "json",
        }
        try:
            data = await self.http_client.get_json(
                self.SEARCH_ENDPOINT,
                params=params,
                source_id=self.source_id,
                ttl_seconds=300,
            )
            if isinstance(data, dict) and "response" in data:
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Internet Archive Advanced Search API is operational",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "IA response missing 'response' payload structure",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Internet Archive connection error: {exc}",
            }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Internet Archive for digitised books, folklore collections, or articles."""
        bounded_limit = min(limit, 50)
        # Search texts or audio related to query
        search_query = f"(mediatype:texts OR mediatype:audio) AND ({query})"
        params = {
            "q": search_query,
            "fl[]": ["identifier", "title", "creator", "publicdate", "description", "licenseurl", "mediatype"],
            "rows": bounded_limit,
            "output": "json",
        }

        data = await self.http_client.get_json(self.SEARCH_ENDPOINT, params=params, source_id=self.source_id)
        if not isinstance(data, dict) or "response" not in data or "docs" not in data["response"]:
            if isinstance(data, dict) and data.get("response", {}).get("numFound") == 0:
                return []
            raise PayloadValidationError("Invalid response format from Internet Archive", source_id=self.source_id)

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-ia-default")

        for doc in data["response"]["docs"]:
            try:
                candidate = self.normalize_record(
                    doc,
                    batch_id=batch_id,
                    proposed_country_code=country_code,
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Retrieve full item metadata from Internet Archive Metadata API."""
        url = f"{self.METADATA_ENDPOINT}/{external_id}"
        try:
            data = await self.http_client.get_json(url, source_id=self.source_id)
            if not isinstance(data, dict) or "metadata" not in data:
                return None
            meta = data["metadata"]
            meta["identifier"] = external_id
            return self.normalize_record(meta, batch_id="batch-ia-single")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert Internet Archive document metadata into an ImportCandidate."""
        identifier = raw_item.get("identifier") or ""
        title = raw_item.get("title") or identifier or "Untitled IA Item"
        if isinstance(title, list) and title:
            title = str(title[0])

        canonical_url = f"{self.BASE_DETAILS_URL}/{identifier}"
        candidate_id = f"CAND-IA-{identifier}"

        # Summary / description
        description = raw_item.get("description") or ""
        if isinstance(description, list) and description:
            description = " ".join(str(d) for d in description)
        clean_desc = re.sub(r"<[^>]+>", "", str(description)).strip()
        summary = clean_desc[:500] if clean_desc else f"Digitised collection item from Internet Archive: {title}"

        # Rights check
        license_url = raw_item.get("licenseurl") or ""
        public_date = str(raw_item.get("publicdate") or raw_item.get("date") or "")
        is_pre_1929 = False
        years = re.findall(r"\b(1[789][0-9]{2}|19[012][0-9])\b", public_date)
        if years and int(years[0]) <= 1928:
            is_pre_1929 = True

        if is_pre_1929 or "publicdomain" in license_url.lower() or "cc0" in license_url.lower():
            rights_status = RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
        else:
            rights_status = RightsStatusEnum.METADATA_ONLY

        review_notes = (
            f"Internet Archive item ({identifier}). Date: {public_date}. "
            "Full text OCR is not ingested into public dataset; bibliographic citation and summary only."
        )

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=identifier,
            raw_title=title,
            raw_language="en",
            raw_url=canonical_url,
            raw_metadata={
                "identifier": identifier,
                "creator": raw_item.get("creator"),
                "publicdate": public_date,
                "licenseurl": license_url,
                "mediatype": raw_item.get("mediatype"),
            },
            raw_text_available=False,
            rights_status=rights_status,
            proposed_country_code=proposed_country_code,
            proposed_category=proposed_category,
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
