"""Tests for Library of Congress JSON API Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import PayloadValidationError
from app.integrations.library_of_congress import LibraryOfCongressConnector
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_loc_response():
    return {
        "results": [
            {
                "id": "http://www.loc.gov/item/95861111/",
                "title": ["Paul Bunyan and Babe the Blue Ox"],
                "contributors": ["Stevens, James"],
                "date": "1925",
                "description": ["Tall tales of the American lumberjack frontier."],
                "url": "https://www.loc.gov/item/95861111/",
                "original_format": ["book"],
                "rights": ["No known restrictions on publication."],
            },
            {
                "id": "http://www.loc.gov/item/2004001234/",
                "title": ["Modern American Folklore Survey"],
                "date": "1985",
                "url": "https://www.loc.gov/item/2004001234/",
                "rights": ["Copyrighted; permission required."],
            },
        ]
    }


@pytest.mark.asyncio
async def test_loc_search_success(mock_loc_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_loc_response

    connector = LibraryOfCongressConnector(http_client=mock_client)
    candidates = await connector.search(
        query="Paul Bunyan",
        country_code="US",
        category=CategoryEnum.FOLKLORE,
        limit=10,
    )

    assert len(candidates) == 2

    # Pre-1929 item
    cand1 = candidates[0]
    assert isinstance(cand1, ImportCandidate)
    assert cand1.raw_title == "Paul Bunyan and Babe the Blue Ox"
    assert cand1.source_registry_id == "library_of_congress_api"
    assert cand1.proposed_country_code == "US"
    assert cand1.rights_status == RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
    assert "Tall tales of the American lumberjack frontier" in (cand1.proposed_summary or "")

    # Post-1929 item
    cand2 = candidates[1]
    assert cand2.rights_status == RightsStatusEnum.METADATA_ONLY


@pytest.mark.asyncio
async def test_loc_empty_results():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"results": []}

    connector = LibraryOfCongressConnector(http_client=mock_client)
    res = await connector.search(query="nothinghere")
    assert res == []


@pytest.mark.asyncio
async def test_loc_malformed_response():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"bad": "data"}

    connector = LibraryOfCongressConnector(http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="fail")
