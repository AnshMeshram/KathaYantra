"""Source Registry Access and Integration Manager for KathaYantra."""

import json
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.schemas.source import SourceApiStatusEnum, SourceRegistryItem


class SourceRegistryManager:
    """Manages inspectable external sources, public datasets, and APIs."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.registry_file = registry_file or (settings.SEED_DIR / "source_registry.json")
        self._sources: dict[str, SourceRegistryItem] = {}
        self.load_sources()

    def load_sources(self) -> None:
        """Load sources from JSON file and validate with Pydantic."""
        if not self.registry_file.exists():
            self._sources = {}
            return

        with open(self.registry_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._sources = {
                item["id"]: SourceRegistryItem.model_validate(item) for item in data
            }

    def list_sources(self) -> list[SourceRegistryItem]:
        """Return all registered sources."""
        return list(self._sources.values())

    def get_source(self, source_id: str) -> Optional[SourceRegistryItem]:
        """Retrieve a specific registered source by slug ID."""
        return self._sources.get(source_id)

    def filter_by_status(self, status: SourceApiStatusEnum) -> list[SourceRegistryItem]:
        """Filter sources by API or access status."""
        return [s for s in self._sources.values() if s.api_status == status]

    def filter_by_country(self, country_code: str) -> list[SourceRegistryItem]:
        """Filter sources covering a specific ISO country code or Global."""
        upper = country_code.upper()
        return [
            s
            for s in self._sources.values()
            if upper in s.geographic_or_cultural_coverage
            or "Global" in s.geographic_or_cultural_coverage
        ]

    def get_status_summary(self) -> dict[str, int]:
        """Return breakdown of sources by API integration status."""
        summary: dict[str, int] = {}
        for s in self._sources.values():
            key = s.api_status.value
            summary[key] = summary.get(key, 0) + 1
        return summary

    def get_connector(self, source_id: str):
        """Instantiate and return the appropriate connector instance for a registered source."""
        from app.integrations.base import BaseConnector
        from app.integrations.csv_importer import CSVFolktalesImporter
        from app.integrations.europeana import EuropeanaConnector
        from app.integrations.internet_archive import InternetArchiveConnector
        from app.integrations.japan_search import JapanSearchConnector
        from app.integrations.library_of_congress import LibraryOfCongressConnector
        from app.integrations.mediawiki import MediaWikiConnector
        from app.integrations.myths_of_ireland import MythsOfIrelandConnector
        from app.integrations.reference_only import ReferenceOnlyConnector
        from app.integrations.wikidata import WikidataConnector

        reg_item = self.get_source(source_id)

        if source_id in ("wikimedia_wikipedia_api", "wikipedia_urban_legends_category"):
            return MediaWikiConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "wikidata_sparql":
            return WikidataConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "library_of_congress_api":
            return LibraryOfCongressConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "internet_archive":
            return InternetArchiveConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "myths_of_ireland":
            return MythsOfIrelandConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "europeana_api":
            return EuropeanaConnector(source_id=source_id, registry_item=reg_item)
        if source_id == "japan_search":
            return JapanSearchConnector(source_id=source_id, registry_item=reg_item)
        if source_id in ("fairytalez_raw_corpus", "csv_raw_corpus"):
            return CSVFolktalesImporter(source_id=source_id, registry_item=reg_item)

        # Fallback to safe ReferenceOnlyConnector
        return ReferenceOnlyConnector(source_id=source_id, registry_item=reg_item)


source_registry_manager = SourceRegistryManager()

