"""KathaYantra Pydantic v2 Canonical Schemas Package."""

from app.schemas.country import (
    CountryCodeEnum,
    CountryRecord,
    CountryRecordTargets,
    SUPPORTED_COUNTRY_CODES,
)
from app.schemas.dataset import (
    CountrySeedFile,
    DatasetEnvelope,
    DatasetMetadata,
)
from app.schemas.generated_fiction import (
    GeneratedFictionRecord,
)
from app.schemas.import_candidate import (
    CandidateDispositionEnum,
    ImportCandidate,
)
from app.schemas.manifest import (
    ActualCounts,
    DatasetManifest,
    TargetBreakdown,
)
from app.schemas.source import (
    RightsStatusEnum,
    SourceApiStatusEnum,
    SourceRegistryItem,
    StorySource,
    validate_web_url,
)
from app.schemas.story import (
    CategoryEnum,
    ContentOriginEnum,
    StoryRecord,
    VerificationStatusEnum,
    generate_slug,
)

__all__ = [
    # Country
    "CountryCodeEnum",
    "CountryRecord",
    "CountryRecordTargets",
    "SUPPORTED_COUNTRY_CODES",
    # Story
    "CategoryEnum",
    "VerificationStatusEnum",
    "RightsStatusEnum",
    "ContentOriginEnum",
    "StorySource",
    "StoryRecord",
    "generate_slug",
    "validate_web_url",
    # Source & Registry
    "SourceApiStatusEnum",
    "SourceRegistryItem",
    # Import Candidate
    "CandidateDispositionEnum",
    "ImportCandidate",
    # AI Fiction
    "GeneratedFictionRecord",
    # Dataset Envelope
    "DatasetEnvelope",
    "DatasetMetadata",
    "CountrySeedFile",
    # Manifest
    "DatasetManifest",
    "TargetBreakdown",
    "ActualCounts",
]
