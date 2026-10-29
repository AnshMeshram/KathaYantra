"""Tests for Japan Search Platform Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import PayloadValidationError
from app.integrations.japan_search import JapanSearchConnector
from app.schemas.import_candidate import ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_jps_response():
    return {
        "hit": 1,
        "items": [
            {
                "id": "ndl_yokai_001",
                "title": "百鬼夜行絵巻 (Night Parade of One Hundred Demons)",
                "link": "https://jpsearch.go.jp/item/ndl_yokai_001",
                "description": "Muromachi-period emakimono depicting Japanese yōkai.",
                "database": "NDL Digital Collections",
            }
        ],
    }


@pytest.mark.asyncio
async def test_japan_search_success(mock_jps_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_jps_response

    connector = JapanSearchConnector(http_client=mock_client)
    candidates = await connector.search(query="百鬼夜行", limit=5)

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, ImportCandidate)
    assert cand.candidate_id == "CAND-JPS-ndl_yokai_001"
    assert cand.external_id == "ndl_yokai_001"
    assert "百鬼夜行絵巻" in cand.raw_title
    assert cand.proposed_country_code == "JP"
    assert cand.proposed_category == CategoryEnum.FOLKLORE
    assert cand.source_registry_id == "japan_search"
    assert cand.rights_status == RightsStatusEnum.METADATA_ONLY


@pytest.mark.asyncio
async def test_japan_search_empty():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"hit": 0, "items": []}

    connector = JapanSearchConnector(http_client=mock_client)
    candidates = await connector.search(query="nonexistent")
    assert candidates == []


@pytest.mark.asyncio
async def test_japan_search_malformed():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"bad_payload": True}

    connector = JapanSearchConnector(http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="error")
