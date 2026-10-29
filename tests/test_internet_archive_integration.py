"""Tests for Internet Archive Advanced Search and Metadata Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import PayloadValidationError
from app.integrations.internet_archive import InternetArchiveConnector
from app.schemas.import_candidate import ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_ia_response():
    return {
        "response": {
            "numFound": 1,
            "docs": [
                {
                    "identifier": "irishfairytales00step",
                    "title": "Irish Fairy Tales",
                    "creator": "Stephens, James",
                    "publicdate": "1920-01-01",
                    "description": "Illustrated classic Irish folklore collection.",
                    "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/",
                    "mediatype": "texts",
                }
            ],
        }
    }


@pytest.mark.asyncio
async def test_internet_archive_search_success(mock_ia_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_ia_response

    connector = InternetArchiveConnector(http_client=mock_client)
    candidates = await connector.search(
        query="Irish Fairy Tales",
        country_code="IE",
        category=CategoryEnum.FOLKLORE,
        limit=5,
    )

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, ImportCandidate)
    assert cand.candidate_id == "CAND-IA-irishfairytales00step"
    assert cand.external_id == "irishfairytales00step"
    assert cand.raw_title == "Irish Fairy Tales"
    assert cand.raw_url == "https://archive.org/details/irishfairytales00step"
    assert cand.rights_status == RightsStatusEnum.PUBLIC_DOMAIN_VERIFIED
    assert cand.source_registry_id == "internet_archive"
    assert "Illustrated classic Irish folklore" in (cand.proposed_summary or "")


@pytest.mark.asyncio
async def test_internet_archive_empty_results():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"response": {"numFound": 0, "docs": []}}

    connector = InternetArchiveConnector(http_client=mock_client)
    res = await connector.search(query="nonexistent")
    assert res == []


@pytest.mark.asyncio
async def test_internet_archive_malformed_response():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"invalid": 123}

    connector = InternetArchiveConnector(http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="error")
