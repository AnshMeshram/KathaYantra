"""Tests for Source Registry Connector Mapping and Health Checks."""

import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.integrations.base import RateLimitError
from app.integrations.http_client import KathaHTTPClient
from app.integrations.registry import source_registry_manager
from app.schemas.story import CategoryEnum


@pytest.mark.asyncio
async def test_reference_only_source_prohibits_bulk_scraping():
    """Verify that Urban Legends Online connector does NOT scrape full-text by default."""
    connector = source_registry_manager.get_connector("urban_legends_online")
    health = await connector.check_health()

    assert health["status"] == "reference_only"
    assert health["bulk_api_supported"] is False

    # Search without manual input returns empty list rather than scraping
    results = await connector.search(query="Bloody Mary", limit=10)
    assert results == []


@pytest.mark.asyncio
async def test_specialist_archives_have_reference_only_status():
    """Verify national and specialist archives lacking bulk APIs are classified reference-only."""
    for src_id in ("ncaa_india", "nichibunken_yokai_db", "duchas_ireland", "cnfcp_iphan_brazil", "folklore_ai_github"):
        connector = source_registry_manager.get_connector(src_id)
        health = await connector.check_health()
        assert health["status"] == "reference_only"
        assert connector.is_reference_only is True


def test_registry_connector_factory_mappings():
    """Ensure all core registered sources instantiate their correct connector types."""
    from app.integrations.csv_importer import CSVFolktalesImporter
    from app.integrations.europeana import EuropeanaConnector
    from app.integrations.internet_archive import InternetArchiveConnector
    from app.integrations.japan_search import JapanSearchConnector
    from app.integrations.library_of_congress import LibraryOfCongressConnector
    from app.integrations.mediawiki import MediaWikiConnector
    from app.integrations.myths_of_ireland import MythsOfIrelandConnector
    from app.integrations.reference_only import ReferenceOnlyConnector
    from app.integrations.wikidata import WikidataConnector

    assert isinstance(source_registry_manager.get_connector("wikimedia_wikipedia_api"), MediaWikiConnector)
    assert isinstance(source_registry_manager.get_connector("wikidata_sparql"), WikidataConnector)
    assert isinstance(source_registry_manager.get_connector("library_of_congress_api"), LibraryOfCongressConnector)
    assert isinstance(source_registry_manager.get_connector("internet_archive"), InternetArchiveConnector)
    assert isinstance(source_registry_manager.get_connector("myths_of_ireland"), MythsOfIrelandConnector)
    assert isinstance(source_registry_manager.get_connector("europeana_api"), EuropeanaConnector)
    assert isinstance(source_registry_manager.get_connector("japan_search"), JapanSearchConnector)
    assert isinstance(source_registry_manager.get_connector("fairytalez_raw_corpus"), CSVFolktalesImporter)
    assert isinstance(source_registry_manager.get_connector("urban_legends_online"), ReferenceOnlyConnector)


@pytest.mark.asyncio
async def test_http_client_handles_rate_limiting():
    """Verify KathaHTTPClient raises RateLimitError on HTTP 429 when Retry-After is large."""
    client = KathaHTTPClient(max_retries=1)

    mock_resp = httpx.Response(
        status_code=429,
        headers={"Retry-After": "60"},
        request=httpx.Request("GET", "https://example.com/api"),
    )

    with patch.object(client._get_client(), "get", new=AsyncMock(return_value=mock_resp)):
        with pytest.raises(RateLimitError) as exc_info:
            await client.get_json("https://example.com/api", use_cache=False)
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    await client.close()
