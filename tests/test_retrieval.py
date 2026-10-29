"""Tests for KathaYantra Deterministic Lexical Retrieval Service."""

import pytest
from app.schemas.story import CategoryEnum
from app.services.retrieval import RetrievalResultItem, retrieval_service


def test_retrieval_exact_keyword_search():
    """Verify keyword searches locate known cultural entities."""
    results = retrieval_service.search("banshee", limit=5)
    assert len(results) >= 1
    top = results[0]
    assert isinstance(top, RetrievalResultItem)
    assert "banshee" in top.title.lower() or "banshee" in top.summary.lower()
    assert top.score >= 0.5
    assert len(top.sources) >= 1
    assert top.sources[0].url.startswith(("http://", "https://"))


def test_retrieval_with_country_filter():
    """Verify country filter restricts returned results strictly to target ISO code."""
    jp_results = retrieval_service.search("spirit", country_code="JP", limit=5)
    assert len(jp_results) >= 1
    for r in jp_results:
        assert r.country_code == "JP"


def test_retrieval_with_category_filter():
    """Verify category filter separates folklore from urban legends."""
    urban_results = retrieval_service.search("ghost", category=CategoryEnum.URBAN_LEGEND, limit=5)
    assert len(urban_results) >= 1
    for r in urban_results:
        assert r.category == CategoryEnum.URBAN_LEGEND


def test_retrieval_no_matches_for_nonsensical_query():
    """Verify nonsensical or unrepresented queries return empty list."""
    results = retrieval_service.search("xyzzy12349876nonexistententity", limit=5)
    assert len(results) == 0


def test_retrieval_get_by_id():
    """Verify direct lookup by canonical story ID."""
    item = retrieval_service.get_by_id("US-URBAN-001")
    assert item is not None
    assert item.story_id == "US-URBAN-001"
    assert "Mothman" in item.title
    assert item.country_code == "US"


def test_retrieval_get_multiple_by_ids():
    """Verify batch lookup of multiple story IDs."""
    items = retrieval_service.get_multiple_by_ids(["IN-FOLK-001", "IE-FOLK-001", "NONEXISTENT-999"])
    found_ids = {it.story_id for it in items}
    assert "IN-FOLK-001" in found_ids
    assert "IE-FOLK-001" in found_ids
    assert "NONEXISTENT-999" not in found_ids


def test_retrieval_sanitizes_punctuation():
    """Verify search does not crash or raise syntax errors on special punctuation."""
    results = retrieval_service.search("what is the 'Mothman' of Point Pleasant??? (West Virginia!)", limit=3)
    assert len(results) >= 1
    assert any("mothman" in r.title.lower() for r in results)

