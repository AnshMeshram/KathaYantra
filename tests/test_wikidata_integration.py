"""Tests for Wikidata SPARQL Endpoint Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import PayloadValidationError
from app.integrations.wikidata import WikidataConnector
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_sparql_response():
    return {
        "results": {
            "bindings": [
                {
                    "item": {"type": "uri", "value": "http://www.wikidata.org/entity/Q214155"},
                    "itemLabel": {"xml:lang": "en", "type": "literal", "value": "Kitsune"},
                    "itemDescription": {
                        "xml:lang": "en",
                        "type": "literal",
                        "value": "fox spirit in Japanese folklore",
                    },
                    "article": {
                        "type": "uri",
                        "value": "https://en.wikipedia.org/wiki/Kitsune",
                    },
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_wikidata_search_success(mock_sparql_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_sparql_response

    connector = WikidataConnector(http_client=mock_client)
    candidates = await connector.search(
        query="Kitsune",
        country_code="JP",
        category=CategoryEnum.FOLKLORE,
        limit=5,
        batch_id="test-wd-batch",
    )

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, ImportCandidate)
    assert cand.candidate_id == "CAND-WD-Q214155"
    assert cand.external_id == "Q214155"
    assert cand.raw_title == "Kitsune"
    assert cand.raw_url == "https://www.wikidata.org/wiki/Q214155"
    assert cand.source_registry_id == "wikidata_sparql"
    assert cand.rights_status == RightsStatusEnum.APPROVED  # CC0
    assert cand.proposed_country_code == "JP"
    assert cand.disposition == CandidateDispositionEnum.NEW_CANDIDATE
    assert "fox spirit in Japanese folklore" in (cand.proposed_summary or "")


@pytest.mark.asyncio
async def test_wikidata_get_by_id(mock_sparql_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_sparql_response

    connector = WikidataConnector(http_client=mock_client)
    cand = await connector.get_by_id("Q214155")
    assert cand is not None
    assert cand.external_id == "Q214155"
    assert cand.raw_title == "Kitsune"


@pytest.mark.asyncio
async def test_wikidata_malformed_response():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"error": "bad query"}

    connector = WikidataConnector(http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="bad")
