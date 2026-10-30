"""Unit and Integration Tests for Archival Pack Export."""

import io
import json
import zipfile
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_export_folklore_pack():
    """Test generating a global folklore archive pack."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/export/pack?category=folklore")
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/zip"
        assert "attachment; filename=\"kathayantra-folklore-archive.zip\"" in res.headers["content-disposition"]
        assert res.headers["x-archive-count"] == "150"

        # Inspect zip structure
        zf = zipfile.ZipFile(io.BytesIO(res.content))
        filenames = zf.namelist()
        assert "KathaYantra-Archive/README.md" in filenames
        assert "KathaYantra-Archive/archive-manifest.json" in filenames
        assert "KathaYantra-Archive/stories.json" in filenames
        assert "KathaYantra-Archive/stories.csv" in filenames
        assert "KathaYantra-Archive/sources/source-manifest.json" in filenames
        assert "KathaYantra-Archive/images/image-attribution.json" in filenames

        # Verify JSON parsed correctly
        stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
        assert len(stories) == 150
        for s in stories:
            assert s["category"] == "folklore"


@pytest.mark.asyncio
async def test_export_urban_legend_pack():
    """Test generating a global urban legends archive pack."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/export/pack?category=urban_legend")
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/zip"
        assert "attachment; filename=\"kathayantra-urban-legend-archive.zip\"" in res.headers["content-disposition"]
        assert res.headers["x-archive-count"] == "150"

        zf = zipfile.ZipFile(io.BytesIO(res.content))
        stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
        assert len(stories) == 150
        for s in stories:
            assert s["category"] == "urban_legend"


@pytest.mark.asyncio
async def test_export_country_pack():
    """Test country-specific folklore pack (e.g. IN)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/export/pack?category=folklore&country_code=IN")
        assert res.status_code == 200
        assert "kathayantra-IN-folklore-archive.zip" in res.headers["content-disposition"]
        assert res.headers["x-archive-count"] == "10"

        zf = zipfile.ZipFile(io.BytesIO(res.content))
        stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
        assert len(stories) == 10
        for s in stories:
            assert s["country_code"] == "IN"
            assert s["category"] == "folklore"


@pytest.mark.asyncio
async def test_export_unsupported_country():
    """Test requesting unsupported country code returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/export/pack?country_code=ZZ")
        assert res.status_code == 404
        data = res.json()
        assert data["error_code"] == "COUNTRY_NOT_SUPPORTED"


@pytest.mark.asyncio
async def test_export_invalid_category():
    """Test requesting invalid category returns 422 validation error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/export/pack?category=aliens")
        assert res.status_code == 422
