"""Comprehensive Unit and Integration Tests for KathaYantra Phase 6 REST API Endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
def client_fixture():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_security_headers_present():
    """Verify security headers are attached to all API responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert resp.headers.get("x-xss-protection") == "1; mode=block"
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


# --- Countries Endpoints ---

@pytest.mark.asyncio
async def test_list_countries_endpoint():
    """Verify GET /api/v1/countries returns all 15 supported countries."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/countries")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "pagination" in body
        assert body["pagination"]["total"] == 15
        assert len(body["data"]) == 15
        codes = [c["code"] for c in body["data"]]
        assert "IN" in codes
        assert "JP" in codes
        assert "BR" in codes


@pytest.mark.asyncio
async def test_get_country_endpoint_valid_and_invalid():
    """Verify GET /api/v1/countries/{country_code} handles existing and unknown countries."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Valid country
        resp = await ac.get("/api/v1/countries/IN")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["code"] == "IN"
        assert data["name"] == "India"

        # Case normalization
        resp_lower = await ac.get("/api/v1/countries/in")
        assert resp_lower.status_code == 200

        # Invalid country
        resp_err = await ac.get("/api/v1/countries/ZZ")
        assert resp_err.status_code == 404
        err_body = resp_err.json()
        assert err_body["error_code"] == "COUNTRY_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_country_stats_endpoint():
    """Verify GET /api/v1/countries/{country_code}/stats calculates exact published metrics."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/countries/JP/stats")
        assert resp.status_code == 200
        stats = resp.json()["data"]
        assert stats["country_code"] == "JP"
        assert stats["folklore_count"] == 10
        assert stats["urban_legend_count"] == 10
        assert stats["total_count"] == 20
        assert stats["folklore_gap"] == 0
        assert stats["urban_legend_gap"] == 0
        assert stats["is_quotas_met"] is True
        assert stats["source_count"] >= 10


@pytest.mark.asyncio
async def test_list_country_stories_with_filters():
    """Verify GET /api/v1/countries/{country_code}/stories supports category and search filtering."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # All stories for Brazil (10 folklore + 10 urban = 20)
        resp_all = await ac.get("/api/v1/countries/BR/stories?limit=50")
        assert resp_all.status_code == 200
        assert resp_all.json()["pagination"]["total"] == 20

        # Folklore only for Brazil
        resp_folk = await ac.get("/api/v1/countries/BR/stories?category=folklore")
        assert resp_folk.status_code == 200
        assert resp_folk.json()["pagination"]["total"] == 10
        assert all(s["category"] == "folklore" for s in resp_folk.json()["data"])

        # Unknown country returns 404
        resp_err = await ac.get("/api/v1/countries/XX/stories")
        assert resp_err.status_code == 404


# --- Folklore Endpoints ---

@pytest.mark.asyncio
async def test_folklore_collection_and_detail():
    """Verify GET /api/v1/folklore and GET /api/v1/folklore/{story_id}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Collection endpoint
        resp = await ac.get("/api/v1/folklore?country_code=IE")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 10
        assert all(s["category"] == "folklore" for s in body["data"])

        # Detail endpoint for authentic folklore
        resp_detail = await ac.get("/api/v1/folklore/IE-FOLK-001")
        assert resp_detail.status_code == 200
        story = resp_detail.json()["data"]
        assert story["id"] == "IE-FOLK-001"
        assert story["category"] == "folklore"
        assert len(story["sources"]) >= 1

        # Asking for an urban legend via /folklore returns 404
        resp_mismatch = await ac.get("/api/v1/folklore/IE-URBAN-001")
        assert resp_mismatch.status_code == 404
        assert resp_mismatch.json()["error_code"] == "STORY_NOT_FOUND"

        # Asking for nonexistent ID returns 404
        resp_none = await ac.get("/api/v1/folklore/IE-FOLK-999")
        assert resp_none.status_code == 404


# --- Urban Legends Endpoints ---

@pytest.mark.asyncio
async def test_urban_legends_collection_and_detail():
    """Verify GET /api/v1/urban-legends and GET /api/v1/urban-legends/{story_id}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Collection endpoint
        resp = await ac.get("/api/v1/urban-legends?country_code=MX")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pagination"]["total"] == 10
        assert all(s["category"] == "urban_legend" for s in body["data"])

        # Detail endpoint
        resp_detail = await ac.get("/api/v1/urban-legends/MX-URBAN-001")
        assert resp_detail.status_code == 200
        story = resp_detail.json()["data"]
        assert story["id"] == "MX-URBAN-001"
        assert story["category"] == "urban_legend"

        # Asking for folklore via /urban-legends returns 404
        resp_mismatch = await ac.get("/api/v1/urban-legends/MX-FOLK-001")
        assert resp_mismatch.status_code == 404
        assert resp_mismatch.json()["error_code"] == "STORY_NOT_FOUND"


# --- Unified Story Endpoints ---

@pytest.mark.asyncio
async def test_stories_unified_endpoints():
    """Verify unified /api/v1/stories/{story_id}, sources, and related narratives."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Unified story lookup (resolves folklore)
        resp_f = await ac.get("/api/v1/stories/IN-FOLK-001")
        assert resp_f.status_code == 200
        assert resp_f.json()["data"]["id"] == "IN-FOLK-001"

        # Unified story lookup (resolves urban legend)
        resp_u = await ac.get("/api/v1/stories/IN-URBAN-001")
        assert resp_u.status_code == 200
        assert resp_u.json()["data"]["id"] == "IN-URBAN-001"

        # Nonexistent story returns 404
        resp_none = await ac.get("/api/v1/stories/IN-FOLK-999")
        assert resp_none.status_code == 404

        # Sources endpoint
        resp_src = await ac.get("/api/v1/stories/IN-FOLK-001/sources")
        assert resp_src.status_code == 200
        sources = resp_src.json()["data"]
        assert len(sources) >= 1
        assert sources[0]["url"] is not None

        # Related stories endpoint
        resp_rel = await ac.get("/api/v1/stories/IN-FOLK-001/related?limit=3")
        assert resp_rel.status_code == 200
        related = resp_rel.json()["data"]
        assert len(related) <= 3
        if related:
            assert "relationship_basis" in related[0]
            assert related[0]["story_id"] != "IN-FOLK-001"


# --- Search and Autocomplete Endpoints ---

@pytest.mark.asyncio
async def test_search_and_suggest_endpoints():
    """Verify GET /api/v1/search and GET /api/v1/search/suggest."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Search for Saci
        resp_search = await ac.get("/api/v1/search?q=Saci")
        assert resp_search.status_code == 200
        body = resp_search.json()
        assert body["pagination"]["total"] >= 1
        assert any("Saci" in s["title"] for s in body["data"])

        # Filtered search
        resp_filt = await ac.get("/api/v1/search?q=Fox&country_code=JP")
        assert resp_filt.status_code == 200
        assert all(s["country_code"] == "JP" for s in resp_filt.json()["data"])

        # Nonsense search returns 0 results cleanly (no synthetic fiction generated)
        resp_empty = await ac.get("/api/v1/search?q=ZorgonMartianFromOuterSpace999")
        assert resp_empty.status_code == 200
        assert resp_empty.json()["pagination"]["total"] == 0
        assert len(resp_empty.json()["data"]) == 0

        # Suggestions endpoint
        resp_sugg = await ac.get("/api/v1/search/suggest?q=Fox")
        assert resp_sugg.status_code == 200
        suggestions = resp_sugg.json()["data"]
        assert len(suggestions) >= 1
        assert any("Fox" in s["text"] or "Kitsune" in s["text"] for s in suggestions)


# --- Source Registry Endpoints ---

@pytest.mark.asyncio
async def test_source_registry_endpoints():
    """Verify GET /api/v1/sources and GET /api/v1/sources/{source_id} without leaking secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # List sources
        resp = await ac.get("/api/v1/sources")
        assert resp.status_code == 200
        sources = resp.json()["data"]
        assert len(sources) >= 17
        for s in sources:
            assert "api_key" not in s
            assert "secret" not in s

        # Specific source
        resp_item = await ac.get("/api/v1/sources/wikimedia_wikipedia_api")
        assert resp_item.status_code == 200
        src = resp_item.json()["data"]
        assert src["id"] == "wikimedia_wikipedia_api"

        # Unknown source returns 404
        resp_err = await ac.get("/api/v1/sources/non_existent_source")
        assert resp_err.status_code == 404


# --- Dataset Governance Endpoints ---

@pytest.mark.asyncio
async def test_dataset_manifest_and_coverage_endpoints():
    """Verify GET /api/v1/dataset/manifest and /api/v1/dataset/coverage."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Manifest
        resp_man = await ac.get("/api/v1/dataset/manifest")
        assert resp_man.status_code == 200
        manifest = resp_man.json()["data"]
        assert manifest["current_actual_counts"]["total_records"] == 300
        assert manifest["required_record_count"] == 300

        # Coverage report
        resp_cov = await ac.get("/api/v1/dataset/coverage")
        assert resp_cov.status_code == 200
        cov = resp_cov.json()["data"]
        assert cov["actual_total_records"] == 300
        assert cov["completion_percentage"] == 100.0
        assert cov["countries_fully_met"] == 15
        assert len(cov["countries"]) == 15


@pytest.mark.asyncio
async def test_dataset_quality_and_readiness_endpoints():
    """Verify GET /api/v1/dataset/quality and /api/v1/dataset/quality/source-readiness."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Quality report
        resp_qual = await ac.get("/api/v1/dataset/quality")
        assert resp_qual.status_code == 200
        qual = resp_qual.json()["data"]
        assert qual["published_records"] == 300
        assert qual["seed_files_valid"] == 30
        assert qual["retrieval_index_count"] == 300

        # Source readiness report
        resp_ready = await ac.get("/api/v1/dataset/quality/source-readiness")
        assert resp_ready.status_code == 200
        ready = resp_ready.json()["data"]
        assert ready["total_records_audited"] == 300
        assert ready["accepted_for_ai"] == 300
        assert ready["flagged_records_count"] == 0
        assert ready["acceptance_rate_percent"] == 100.0
        assert ready["status"] == "pass"
