"""Tests for KathaYantra External Data Sources and API Registry."""

from pathlib import Path
import pytest
from app.core.config import settings
from app.integrations.registry import source_registry_manager
from app.schemas.source import SourceApiStatusEnum, SourceRegistryItem
from app.schemas.story import RightsStatusEnum


def test_source_registry_schema_validation():
    """Test 14: Validate that all registered sources adhere strictly to the schema."""
    sources = source_registry_manager.list_sources()
    assert len(sources) >= 14, f"Expected at least 14 registered sources, found {len(sources)}"

    # Check that each item is a valid SourceRegistryItem
    for s in sources:
        assert isinstance(s, SourceRegistryItem)
        assert s.id
        assert s.name
        assert s.canonical_url.startswith(("http://", "https://"))
        assert s.docs_or_dataset_url.startswith(("http://", "https://"))
        assert isinstance(s.api_status, SourceApiStatusEnum)
        assert isinstance(s.rights_assessment_status, RightsStatusEnum)
        assert isinstance(s.auth_required, bool)
        assert isinstance(s.full_text_reuse_verified, bool)
        assert isinstance(s.retain_metadata_only, bool)
        assert len(s.geographic_or_cultural_coverage) > 0


def test_required_phase1_sources_present():
    """Verify that all sources explicitly requested in Phase 1 are registered."""
    required_ids = [
        "urban_legends_online",
        "folklore_ai_github",
        "wikimedia_wikipedia_api",
        "wikidata_sparql",
        "library_of_congress_api",
        "internet_archive",
        "myths_of_ireland",
        "nichibunken_yokai_db",
        "japan_search",
        "europeana_api",
        "ncaa_india",
        "duchas_ireland",
        "cnfcp_iphan_brazil",
        "project_gutenberg",
    ]

    for req_id in required_ids:
        source = source_registry_manager.get_source(req_id)
        assert source is not None, f"Required source '{req_id}' is missing from source_registry.json"


def test_honest_access_and_rights_representation():
    """Verify that unverified or scrape-only sources are not claimed as open APIs."""
    # Urban Legends Online must NOT be claimed as a documented working API
    ulo = source_registry_manager.get_source("urban_legends_online")
    assert ulo.api_status == SourceApiStatusEnum.REFERENCE_ONLY
    assert ulo.full_text_reuse_verified is False
    assert ulo.retain_metadata_only is True

    # Folklore-ai must be reference_only
    fai = source_registry_manager.get_source("folklore_ai_github")
    assert fai.api_status == SourceApiStatusEnum.REFERENCE_ONLY
    assert fai.full_text_reuse_verified is False

    # NCAA India has no public REST API
    ncaa = source_registry_manager.get_source("ncaa_india")
    assert ncaa.api_status == SourceApiStatusEnum.SEARCHABLE_CATALOGUE

    # Dúchas Ireland is marked not_yet_verified
    duchas = source_registry_manager.get_source("duchas_ireland")
    assert duchas.api_status == SourceApiStatusEnum.NOT_YET_VERIFIED


def test_filtering_sources():
    """Verify filtering sources by status and country coverage."""
    documented_apis = source_registry_manager.filter_by_status(SourceApiStatusEnum.DOCUMENTED_API)
    assert len(documented_apis) >= 3

    india_sources = source_registry_manager.filter_by_country("IN")
    assert len(india_sources) > 0

    japan_sources = source_registry_manager.filter_by_country("JP")
    assert len(japan_sources) > 0

