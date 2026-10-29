"""Tests for Europeana Digital Cultural Heritage API Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import AuthenticationError, PayloadValidationError
from app.integrations.europeana import EuropeanaConnector
from app.schemas.import_candidate import ImportCandidate
from app.schemas.source import RightsStatusEnum


@pytest.fixture
def mock_europeana_response():
    return {
        "success": True,
        "itemsCount": 2,
        "items": [
            {
                "id": "/9200365/BibliographicResource_1",
                "title": ["Grimm's Fairy Tales (German Edition)"],
                "rights": ["http://creativecommons.org/publicdomain/mark/1.0/"],
                "guid": "https://www.europeana.eu/item/9200365/BibliographicResource_1",
                "description": "Historical collection of German folk stories.",
                "country": ["Germany"],
            },
            {
                "id": "/9200365/ModernStudy_2",
                "title": ["Modern Greek Folklore Commentary"],
                "rights": ["http://rightsstatements.org/vocab/InC/1.0/"],
                "guid": "https://www.europeana.eu/item/9200365/ModernStudy_2",
                "country": ["Greece"],
            },
        ],
    }


@pytest.mark.asyncio
async def test_europeana_missing_key_behavior():
    connector = EuropeanaConnector(api_key="")
    health = await connector.check_health()
    assert health["status"] == "requires_credentials"
    assert "EUROPEANA_API_KEY is not configured" in health["message"]

    # Search should safely return empty list without throwing
    res = await connector.search(query="Grimm")
    assert res == []


@pytest.mark.asyncio
async def test_europeana_with_valid_mock_response(mock_europeana_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_europeana_response

    connector = EuropeanaConnector(api_key="valid-test-key", http_client=mock_client)
    health = await connector.check_health()
    assert health["status"] == "ok"

    candidates = await connector.search(query="Grimm")
    assert len(candidates) == 2

    cand1 = candidates[0]
    assert isinstance(cand1, ImportCandidate)
    assert cand1.raw_title == "Grimm's Fairy Tales (German Edition)"
    assert cand1.rights_status == RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
    assert cand1.source_registry_id == "europeana_api"

    cand2 = candidates[1]
    assert cand2.rights_status == RightsStatusEnum.METADATA_ONLY


@pytest.mark.asyncio
async def test_europeana_auth_failure():
    mock_client = AsyncMock()
    mock_client.get_json.side_effect = AuthenticationError("Invalid WSKey", status_code=401)

    connector = EuropeanaConnector(api_key="bad-key", http_client=mock_client)
    health = await connector.check_health()
    assert health["status"] == "requires_credentials"
    assert "invalid or unauthorized" in health["message"]


@pytest.mark.asyncio
async def test_europeana_malformed_response():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"success": False, "error": "Invalid query syntax"}

    connector = EuropeanaConnector(api_key="valid-key", http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="broken")
