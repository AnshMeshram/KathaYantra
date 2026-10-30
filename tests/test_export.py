"""Unit and Integration Tests for Archival Pack Export."""

import io
import json
import zipfile
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.story_repository import story_repository

# Preload story repository for tests
story_repository.load()
client = TestClient(app)


def test_export_folklore_pack():
    """Test generating a global folklore archive pack."""
    res = client.get("/api/v1/export/pack?category=folklore")
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


def test_export_urban_legend_pack():
    """Test generating a global urban legends archive pack."""
    res = client.get("/api/v1/export/pack?category=urban_legend")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert "attachment; filename=\"kathayantra-urban-legend-archive.zip\"" in res.headers["content-disposition"]
    assert res.headers["x-archive-count"] == "150"

    zf = zipfile.ZipFile(io.BytesIO(res.content))
    stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
    assert len(stories) == 150
    for s in stories:
        assert s["category"] == "urban_legend"


def test_export_country_pack():
    """Test country-specific folklore pack (e.g. IN)."""
    res = client.get("/api/v1/export/pack?category=folklore&country_code=IN")
    assert res.status_code == 200
    assert "kathayantra-IN-folklore-archive.zip" in res.headers["content-disposition"]
    assert res.headers["x-archive-count"] == "10"

    zf = zipfile.ZipFile(io.BytesIO(res.content))
    stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
    assert len(stories) == 10
    for s in stories:
        assert s["country_code"] == "IN"
        assert s["category"] == "folklore"


def test_export_unsupported_country():
    """Test requesting unsupported country code returns 404."""
    res = client.get("/api/v1/export/pack?country_code=ZZ")
    assert res.status_code == 404
    data = res.json()
    assert data["error_code"] == "COUNTRY_NOT_SUPPORTED"


def test_export_invalid_category():
    """Test requesting invalid category returns 422 validation error."""
    res = client.get("/api/v1/export/pack?category=aliens")
    assert res.status_code == 422


if __name__ == "__main__":
    print("Testing test_export_folklore_pack...")
    test_export_folklore_pack()
    print("Testing test_export_urban_legend_pack...")
    test_export_urban_legend_pack()
    print("Testing test_export_country_pack...")
    test_export_country_pack()
    print("Testing test_export_unsupported_country...")
    test_export_unsupported_country()
    print("Testing test_export_invalid_category...")
    test_export_invalid_category()
    print("[PASS] All export tests passed successfully!")

