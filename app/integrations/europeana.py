"""Europeana Digital Cultural Heritage REST API Connector for KathaYantra."""

from typing import Any, Optional
from app.core.config import settings
from app.integrations.base import AuthenticationError, BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class EuropeanaConnector(BaseConnector):
    """Connector for the Europeana Digital Cultural Heritage API."""

    SEARCH_ENDPOINT = "https://api.europeana.eu/record/v2/search.json"
    RECORD_ENDPOINT = "https://api.europeana.eu/record/v2"

    def __init__(
        self,
        source_id: str = "europeana_api",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
        api_key: Optional[str] = None,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()
        self.api_key = api_key if api_key is not None else settings.EUROPEANA_API_KEY

    async def check_health(self) -> dict[str, Any]:
        """Verify Europeana API status and credential configuration."""
        if not self.api_key:
            return {
                "source_id": self.source_id,
                "status": "requires_credentials",
                "message": "EUROPEANA_API_KEY is not configured in environment. Connector is safely dormant.",
            }

        params = {
            "query": "folklore",
            "wskey": self.api_key,
            "rows": 1,
        }
        try:
            data = await self.http_client.get_json(self.SEARCH_ENDPOINT, params=params, source_id=self.source_id)
            if isinstance(data, dict) and data.get("success"):
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Europeana REST API is operational with valid credentials",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": f"Europeana API returned unexpected response: {data}",
            }
        except AuthenticationError:
            return {
                "source_id": self.source_id,
                "status": "requires_credentials",
                "message": "Configured EUROPEANA_API_KEY is invalid or unauthorized (HTTP 401/403)",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"Europeana connection error: {exc}",
            }

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Europeana records. Returns empty list with error logged if credentials missing."""
        if not self.api_key:
            # Safely fail if credentials missing without crashing application
            return []

        bounded_limit = min(limit, 50)
        params = {
            "query": query,
            "wskey": self.api_key,
            "rows": bounded_limit,
        }
        if country_code:
            params["qf"] = f"COUNTRY:{country_code.lower()}"

        data = await self.http_client.get_json(self.SEARCH_ENDPOINT, params=params, source_id=self.source_id)
        if not isinstance(data, dict):
            raise PayloadValidationError("Invalid response from Europeana", source_id=self.source_id)

        if not data.get("success", False):
            raise PayloadValidationError(f"Europeana query failed: {data.get('error', 'Unknown error')}", source_id=self.source_id)

        items = data.get("items", [])
        if not items:
            return []
        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-europeana-default")

        for item in items:
            try:
                candidate = self.normalize_record(
                    item,
                    batch_id=batch_id,
                    proposed_country_code=country_code,
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Retrieve single Europeana record by ID."""
        if not self.api_key:
            return None

        clean_id = external_id.lstrip("/")
        url = f"{self.RECORD_ENDPOINT}/{clean_id}.json"
        params = {"wskey": self.api_key}
        try:
            data = await self.http_client.get_json(url, params=params, source_id=self.source_id)
            if not isinstance(data, dict) or "object" not in data:
                return None
            return self.normalize_record(data["object"], batch_id="batch-europeana-single")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a Europeana record object into an ImportCandidate."""
        item_id = raw_item.get("id") or ""
        clean_ext_id = item_id.replace("/", "_").strip("_")
        candidate_id = f"CAND-EUR-{clean_ext_id}"

        title = raw_item.get("title") or raw_item.get("dcTitleLangAware", {}).get("def", ["Untitled"])[0]
        if isinstance(title, list) and title:
            title = str(title[0])

        canonical_url = raw_item.get("guid") or f"https://www.europeana.eu/item{item_id}"

        # Rights mapping
        edm_rights = raw_item.get("rights") or raw_item.get("edmRights") or []
        rights_str = " ".join(edm_rights) if isinstance(edm_rights, list) else str(edm_rights)
        if "publicdomain" in rights_str.lower() or "/zero/" in rights_str.lower():
            rights_status = RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
        else:
            rights_status = RightsStatusEnum.METADATA_ONLY

        description = raw_item.get("dcDescriptionLangAware", {}).get("def", [""])[0] if isinstance(raw_item.get("dcDescriptionLangAware"), dict) else ""
        if not description and "description" in raw_item:
            description = str(raw_item["description"])
        summary = str(description)[:500] if description else f"European cultural heritage record: {title}"

        country = raw_item.get("country", [""])[0] if isinstance(raw_item.get("country"), list) else str(raw_item.get("country", ""))
        mapped_country = proposed_country_code
        if not mapped_country and country:
            country_clean = country.upper()
            if len(country_clean) == 2:
                mapped_country = country_clean

        review_notes = f"Europeana cultural heritage item ({item_id}). Rights: {rights_str[:120]}. Bibliographic metadata only."

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=item_id,
            raw_title=str(title),
            raw_language="en",
            raw_url=canonical_url,
            raw_metadata={
                "europeana_id": item_id,
                "type": raw_item.get("type"),
                "year": raw_item.get("year"),
                "dataProvider": raw_item.get("dataProvider"),
                "rights": edm_rights,
            },
            raw_text_available=False,
            rights_status=rights_status,
            proposed_country_code=mapped_country,
            proposed_category=proposed_category,
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
