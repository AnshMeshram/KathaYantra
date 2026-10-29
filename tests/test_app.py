"""Tests for KathaYantra FastAPI application startup and health endpoints."""

from fastapi.testclient import TestClient
import pytest
from app.core.config import settings
from app.main import app, create_app


@pytest.fixture
def client():
    """Test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


def test_app_startup(client):
    """Test 1: Application startup and root endpoint response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == settings.PROJECT_NAME
    assert data["version"] == settings.PROJECT_VERSION
    assert "health_endpoint" in data
    assert data["health_endpoint"] == f"{settings.API_V1_PREFIX}/health"


def test_health_endpoint_response(client):
    """Test 2: Health endpoint response structure and status values."""
    response = client.get(f"{settings.API_V1_PREFIX}/health")
    assert response.status_code == 200
    data = response.json()

    # Core health fields
    assert data["status"] in ("ok", "degraded")
    assert data["app_name"] == settings.PROJECT_NAME
    assert data["app_version"] == settings.PROJECT_VERSION
    assert data["config_loaded"] is True

    # Datasets availability
    datasets = data["datasets_available"]
    assert "countries_json" in datasets
    assert "source_registry_json" in datasets
    assert "folklore_seed_dir" in datasets
    assert "urban_legends_seed_dir" in datasets

    # Counts
    counts = data["counts"]
    assert counts["target_countries"] == 15
    assert counts["required_total_stories"] == 300
    assert counts["actual_total_stories"] >= 0

    # Local AI section
    local_ai = data["local_ai"]
    assert local_ai["configured_model"] == settings.OLLAMA_MODEL
    assert "ollama_available" in local_ai
    assert isinstance(local_ai["ollama_available"], bool)


def test_cors_middleware_configured(client):
    """Test CORS headers on options preflight request."""
    response = client.options(
        f"{settings.API_V1_PREFIX}/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

