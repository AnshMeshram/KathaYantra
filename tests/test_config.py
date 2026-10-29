"""Tests for KathaYantra Core Configuration and Path Validation."""

from pathlib import Path
import pytest
from app.core.config import Settings, settings


def test_configuration_validation():
    """Test 3: Configuration validation with defaults and custom parameters."""
    cfg = Settings(
        PROJECT_NAME="CustomKatha",
        OLLAMA_MODEL="gemma2:9b",
        CORS_ORIGINS='["http://localhost:5173", "http://127.0.0.1:5173"]',
        PORT=9000,
    )

    assert cfg.PROJECT_NAME == "CustomKatha"
    assert cfg.OLLAMA_MODEL == "gemma2:9b"
    assert cfg.PORT == 9000
    assert "http://localhost:5173" in cfg.CORS_ORIGINS
    assert cfg.REQUIRED_TOTAL_RECORDS == 300
    assert cfg.TARGET_COUNTRIES_COUNT == 15


def test_cors_origins_comma_separated_parsing():
    """Test parsing comma-separated CORS origins string."""
    cfg = Settings(
        CORS_ORIGINS="http://example.com, http://app.example.com",
    )
    assert "http://example.com" in cfg.CORS_ORIGINS
    assert "http://app.example.com" in cfg.CORS_ORIGINS


def test_missing_dataset_directories(tmp_path: Path):
    """Test 10: Graceful handling of missing dataset directories."""
    non_existent = tmp_path / "does_not_exist"
    cfg = Settings(
        DATA_DIR=non_existent,
        SEED_DIR=non_existent / "seed",
        RAW_DIR=non_existent / "raw",
        MANIFESTS_DIR=non_existent / "manifests",
    )

    # Paths can be accessed without throwing
    assert not cfg.DATA_DIR.exists()
    assert not cfg.folklore_seed_dir.exists()
    assert not cfg.urban_legends_seed_dir.exists()

