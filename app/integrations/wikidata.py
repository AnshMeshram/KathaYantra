"""Wikidata SPARQL Endpoint Connector for KathaYantra."""

from typing import Any, Optional
from app.integrations.base import BaseConnector, PayloadValidationError
from app.integrations.http_client import KathaHTTPClient, get_http_client
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class WikidataConnector(BaseConnector):
    """Connector for querying structured cultural entities via the Wikidata SPARQL endpoint."""

    SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

    def __init__(
        self,
        source_id: str = "wikidata_sparql",
        registry_item: Optional[SourceRegistryItem] = None,
        http_client: Optional[KathaHTTPClient] = None,
        endpoint_url: str = SPARQL_ENDPOINT,
    ):
        super().__init__(source_id, registry_item)
        self.http_client = http_client or get_http_client()
        self.endpoint_url = endpoint_url

    async def check_health(self) -> dict[str, Any]:
        """Verify Wikidata SPARQL endpoint connectivity with a minimal query."""
        minimal_query = "SELECT ?item WHERE { ?item wdt:P31 wd:Q11451 . } LIMIT 1"
        try:
            data = await self._run_sparql(minimal_query, timeout_seconds=10)
            if isinstance(data, dict) and "results" in data:
                return {
                    "source_id": self.source_id,
                    "status": "ok",
                    "message": "Wikidata SPARQL service is operational",
                }
            return {
                "source_id": self.source_id,
                "status": "degraded",
                "message": "SPARQL endpoint responded without expected results structure",
            }
        except Exception as exc:
            return {
                "source_id": self.source_id,
                "status": "unavailable",
                "message": f"SPARQL error: {exc}",
            }

    async def _run_sparql(self, sparql_query: str, timeout_seconds: int = 25) -> dict[str, Any]:
        """Execute a SPARQL query against Wikidata returning results in JSON."""
        headers = {
            "Accept": "application/sparql-results+json",
        }
        params = {
            "query": sparql_query,
            "format": "json",
        }
        return await self.http_client.get_json(
            self.endpoint_url,
            params=params,
            headers=headers,
            source_id=self.source_id,
            ttl_seconds=3600,
        )

    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search Wikidata for folklore or mythical entities matching query term."""
        bounded_limit = min(limit, 50)
        # Bounded query searching label containing term
        sanitized_query = query.replace('"', '\\"')
        sparql = f"""
        SELECT ?item ?itemLabel ?itemDescription ?article WHERE {{
          SERVICE wikibase:mwapi {{
            bd:serviceParam wikibase:endpoint "www.wikidata.org";
                            wikibase:api "EntitySearch";
                            mwapi:search "{sanitized_query}";
                            mwapi:language "en".
            ?item wikibase:apiOutputItem mwapi:item.
          }}
          OPTIONAL {{
            ?article schema:about ?item ;
                     schema:isPartOf <https://en.wikipedia.org/> .
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {bounded_limit}
        """

        data = await self._run_sparql(sparql)
        if not isinstance(data, dict) or "results" not in data or "bindings" not in data["results"]:
            raise PayloadValidationError("Invalid SPARQL results payload from Wikidata", source_id=self.source_id)

        candidates: list[ImportCandidate] = []
        batch_id = kwargs.get("batch_id", "batch-wikidata-default")

        for binding in data["results"]["bindings"]:
            try:
                candidate = self.normalize_record(
                    binding,
                    batch_id=batch_id,
                    proposed_country_code=country_code,
                    proposed_category=category,
                )
                candidates.append(candidate)
            except Exception:
                continue

        return candidates

    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Retrieve entity details by Wikidata QID (e.g. Q214155)."""
        qid = external_id.upper().strip()
        if not qid.startswith("Q") or not qid[1:].isdigit():
            return None

        sparql = f"""
        SELECT ?item ?itemLabel ?itemDescription ?article WHERE {{
          VALUES ?item {{ wd:{qid} }}
          OPTIONAL {{
            ?article schema:about ?item ;
                     schema:isPartOf <https://en.wikipedia.org/> .
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """
        try:
            data = await self._run_sparql(sparql)
            bindings = data.get("results", {}).get("bindings", [])
            if not bindings:
                return None
            return self.normalize_record(bindings[0], batch_id="batch-wikidata-single")
        except Exception:
            return None

    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a SPARQL binding into an ImportCandidate."""
        item_uri = raw_item.get("item", {}).get("value", "")
        qid = item_uri.split("/")[-1] if "/" in item_uri else item_uri
        label = raw_item.get("itemLabel", {}).get("value", qid)
        description = raw_item.get("itemDescription", {}).get("value", "")
        article_url = raw_item.get("article", {}).get("value")

        canonical_url = f"https://www.wikidata.org/wiki/{qid}" if qid.startswith("Q") else item_uri
        candidate_id = f"CAND-WD-{qid}"

        summary = description if description else f"Wikidata entity {label} ({qid})"
        review_notes = "Structured knowledge graph entity from Wikidata. Data is dedicated to the public domain under CC0 1.0."

        return ImportCandidate(
            candidate_id=candidate_id,
            import_batch_id=batch_id,
            source_registry_id=self.source_id,
            external_id=qid,
            raw_title=label,
            raw_language="en",
            raw_url=canonical_url,
            raw_metadata={
                "qid": qid,
                "uri": item_uri,
                "description": description,
                "wikipedia_article": article_url,
                "license": "CC0-1.0",
            },
            raw_text_available=False,
            rights_status=RightsStatusEnum.APPROVED,  # Wikidata structured metadata is CC0
            proposed_country_code=proposed_country_code,
            proposed_category=proposed_category,
            proposed_summary=summary,
            disposition=CandidateDispositionEnum.NEW_CANDIDATE,
            review_notes=review_notes,
        )
