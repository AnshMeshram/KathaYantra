"""Base Connector Interface and Error Hierarchy for KathaYantra Open Data Integrations."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from app.schemas.import_candidate import ImportCandidate
from app.schemas.source import RightsStatusEnum, SourceRegistryItem
from app.schemas.story import CategoryEnum


class ConnectorError(Exception):
    """Base exception for all KathaYantra data connector errors."""

    def __init__(self, message: str, source_id: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.source_id = source_id
        self.status_code = status_code


class RateLimitError(ConnectorError):
    """Raised when upstream API rate limits are exceeded (HTTP 429)."""

    def __init__(self, message: str, source_id: Optional[str] = None, retry_after: Optional[int] = None):
        super().__init__(message, source_id=source_id, status_code=429)
        self.retry_after = retry_after


class AuthenticationError(ConnectorError):
    """Raised when API credentials are missing or invalid (HTTP 401/403)."""

    def __init__(self, message: str, source_id: Optional[str] = None, status_code: int = 401):
        super().__init__(message, source_id=source_id, status_code=status_code)


class NotFoundError(ConnectorError):
    """Raised when an upstream item or endpoint returns 404."""

    def __init__(self, message: str, source_id: Optional[str] = None):
        super().__init__(message, source_id=source_id, status_code=404)


class ConnectionTimeoutError(ConnectorError):
    """Raised when network connection or read timeout expires."""

    def __init__(self, message: str, source_id: Optional[str] = None):
        super().__init__(message, source_id=source_id, status_code=408)


class PayloadValidationError(ConnectorError):
    """Raised when upstream response payload is malformed or unparseable."""

    def __init__(self, message: str, source_id: Optional[str] = None):
        super().__init__(message, source_id=source_id)


class BaseConnector(ABC):
    """Abstract base connector defining standard operations for data source adapters."""

    def __init__(self, source_id: str, registry_item: Optional[SourceRegistryItem] = None):
        self.source_id = source_id
        self.registry_item = registry_item

    @property
    def is_reference_only(self) -> bool:
        """Indicates if this source is restricted to manual/discovery references."""
        if self.registry_item:
            return self.registry_item.api_status.value == "reference_only" or self.registry_item.retain_metadata_only
        return False

    @property
    def requires_auth(self) -> bool:
        """Indicates if upstream access requires an API key or token."""
        if self.registry_item:
            return self.registry_item.auth_required
        return False

    @property
    def default_rights_status(self) -> RightsStatusEnum:
        """Default rights classification for candidate metadata ingested from this source."""
        if self.registry_item:
            return self.registry_item.rights_assessment_status
        return RightsStatusEnum.NEEDS_RIGHTS_REVIEW

    @abstractmethod
    async def check_health(self) -> dict[str, Any]:
        """Perform a non-blocking availability and credential check.

        Returns:
            Dictionary with status ('ok', 'degraded', 'unavailable', 'requires_credentials', 'reference_only')
            and diagnostic message.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> list[ImportCandidate]:
        """Search upstream source for relevant folklore or urban-legend candidate records.

        Args:
            query: Search phrase or query string.
            country_code: Optional ISO alpha-2 country code.
            category: Optional CategoryEnum filter ('folklore' or 'urban_legend').
            limit: Maximum candidate items to return.
            **kwargs: Source-specific options (e.g. language, offset).

        Returns:
            List of normalized ImportCandidate instances.
        """
        pass

    @abstractmethod
    async def get_by_id(self, external_id: str) -> Optional[ImportCandidate]:
        """Fetch a single record by upstream accession or entity ID."""
        pass

    @abstractmethod
    def normalize_record(
        self,
        raw_item: dict[str, Any],
        batch_id: str,
        proposed_country_code: Optional[str] = None,
        proposed_category: Optional[CategoryEnum] = None,
    ) -> ImportCandidate:
        """Convert a raw upstream payload dictionary into a validated ImportCandidate."""
        pass
