"""Tests for MediaWiki / Wikipedia REST API Connector."""

import pytest
from unittest.mock import AsyncMock
from app.integrations.base import PayloadValidationError
from app.integrations.mediawiki import MediaWikiConnector
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_mediawiki_response():
    return {
        "pages": [
            {
                "id": 169992,
                "key": "Kitsune",
                "title": "Kitsune",
                "excerpt": "<span>Kitsune</span> is the Japanese word for the fox.",
                "description": "Japanese fox spirit in folklore",
                "thumbnail": {"url": "https://upload.wikimedia.org/kitsune.jpg"},
            },
            {
                "id": 55432,
                "key": "Tanuki",
                "title": "Tanuki",
                "excerpt": "The <i>Japanese raccoon dog</i> has a significant role in folklore.",
                "description": "Japanese folklore mammal and yōkai",
            },
        ]
    }


@pytest.mark.asyncio
async def test_mediawiki_search_success(mock_mediawiki_response):
    mock_client = AsyncMock()
    mock_client.get_json.return_value = mock_mediawiki_response

    connector = MediaWikiConnector(http_client=mock_client)
    candidates = await connector.search(
        query="Japanese folklore",
        country_code="JP",
        category=CategoryEnum.FOLKLORE,
        limit=10,
        batch_id="test-wiki-batch",
    )

    assert len(candidates) == 2
    cand1 = candidates[0]
    assert isinstance(cand1, ImportCandidate)
    assert cand1.candidate_id == "CAND-WIKI-169992"
    assert cand1.raw_title == "Kitsune"
    assert cand1.raw_url == "https://en.wikipedia.org/wiki/Kitsune"
    assert cand1.proposed_country_code == "JP"
    assert cand1.proposed_category == CategoryEnum.FOLKLORE
    assert cand1.source_registry_id == "wikimedia_wikipedia_api"
    assert cand1.rights_status == RightsStatusEnum.METADATA_ONLY
    assert cand1.disposition == CandidateDispositionEnum.NEW_CANDIDATE
    # HTML stripped from excerpt
    assert "<span>" not in (cand1.proposed_summary or "")
    assert "Kitsune is the Japanese word for the fox." in (cand1.proposed_summary or "")


@pytest.mark.asyncio
async def test_mediawiki_empty_results():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"pages": []}

    connector = MediaWikiConnector(http_client=mock_client)
    candidates = await connector.search(query="NonExistentFolkloreXYZ")
    assert candidates == []


@pytest.mark.asyncio
async def test_mediawiki_malformed_response():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {"unexpected_key": 123}

    connector = MediaWikiConnector(http_client=mock_client)
    with pytest.raises(PayloadValidationError):
        await connector.search(query="test")


@pytest.mark.asyncio
async def test_mediawiki_get_by_id():
    mock_client = AsyncMock()
    mock_client.get_json.return_value = {
        "pageid": 169992,
        "title": "Kitsune",
        "extract": "Kitsune are legendary foxes with supernatural abilities.",
        "content_urls": {
            "desktop": {"page": "https://en.wikipedia.org/wiki/Kitsune"}
        },
    }

    connector = MediaWikiConnector(http_client=mock_client)
    candidate = await connector.get_by_id("Kitsune")
    assert candidate is not None
    assert candidate.raw_title == "Kitsune"
    assert candidate.raw_url == "https://en.wikipedia.org/wiki/Kitsune"
    assert "supernatural abilities" in (candidate.proposed_summary or "")
