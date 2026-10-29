"""Tests for Myths of Ireland Structured Dataset Connector."""

import pytest
from app.integrations.myths_of_ireland import MythsOfIrelandConnector
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate
from app.schemas.source import RightsStatusEnum
from app.schemas.story import CategoryEnum


@pytest.fixture
def mock_moi_items():
    return [
        {
            "id": "children_of_lir",
            "slug": "children-of-lir",
            "title": "The Children of Lir",
            "type": "story",
            "cycle": "Mythological Cycle",
            "summary": "Tragic tale of four siblings transformed into swans by their stepmother Aoife for 900 years.",
            "url": "https://www.mythsofireland.com/stories/children-of-lir",
            "motifs": ["D621.1", "T257.2"],
        },
        {
            "id": "banshee_bean_sidhe",
            "slug": "banshee",
            "title": "Bean Sídhe (The Banshee)",
            "type": "being",
            "summary": "A female spirit in Irish folklore who heralds the death of a family member by keening.",
            "url": "https://www.mythsofireland.com/beings/banshee",
        },
    ]


@pytest.mark.asyncio
async def test_myths_of_ireland_search_with_preloaded_items(mock_moi_items):
    connector = MythsOfIrelandConnector()
    candidates = await connector.search(
        query="Children of Lir",
        preloaded_items=mock_moi_items,
    )

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, ImportCandidate)
    assert cand.candidate_id == "CAND-MOI-children-of-lir"
    assert cand.raw_title == "The Children of Lir"
    assert cand.raw_url == "https://www.mythsofireland.com/stories/children-of-lir"
    assert cand.proposed_country_code == "IE"
    assert cand.proposed_category == CategoryEnum.FOLKLORE
    assert cand.rights_status == RightsStatusEnum.APPROVED
    assert "Myths of Ireland open dataset" in (cand.review_notes or "")


@pytest.mark.asyncio
async def test_myths_of_ireland_entity_type_separation(mock_moi_items):
    connector = MythsOfIrelandConnector()
    candidates = await connector.search(
        query="Banshee",
        preloaded_items=mock_moi_items,
    )

    assert len(candidates) == 1
    cand = candidates[0]
    # Check that supernatural being distinction is recorded in review notes
    assert "supernatural being/character" in (cand.review_notes or "")
