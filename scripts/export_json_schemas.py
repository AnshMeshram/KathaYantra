"""KathaYantra - JSON Schema Draft 2020-12 Exporter.

Exports deterministic JSON Schema Draft 2020-12 specifications
directly from authoritative Pydantic v2 models into data/schemas/.
"""

import json
from pathlib import Path
import sys
from typing import Type

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel
from app.schemas.country import CountryRecord
from app.schemas.dataset import DatasetEnvelope
from app.schemas.generated_fiction import GeneratedFictionRecord
from app.schemas.import_candidate import ImportCandidate
from app.schemas.manifest import DatasetManifest
from app.schemas.source import SourceRegistryItem, StorySource
from app.schemas.story import StoryRecord

DRAFT_2020_12_URI = "https://json-schema.org/draft/2020-12/schema"

MODELS_TO_EXPORT: dict[str, tuple[Type[BaseModel], str]] = {
    "country.schema.json": (
        CountryRecord,
        "Canonical schema contract for KathaYantra country registry entries",
    ),
    "story.schema.json": (
        StoryRecord,
        "Canonical schema contract for KathaYantra folklore narratives and urban legends",
    ),
    "source.schema.json": (
        StorySource,
        "Bibliographic citation and provenance reference schema embedded in stories",
    ),
    "source_registry_item.schema.json": (
        SourceRegistryItem,
        "External data source, repository, and API registration schema",
    ),
    "import_candidate.schema.json": (
        ImportCandidate,
        "Staging schema for raw, unreviewed, or partially processed narrative candidates",
    ),
    "generated_fiction.schema.json": (
        GeneratedFictionRecord,
        "Schema for AI-generated creative fiction inspired by folklore traditions",
    ),
    "dataset_envelope.schema.json": (
        DatasetEnvelope,
        "Canonical envelope schema for country seed dataset files",
    ),
    "dataset_manifest.schema.json": (
        DatasetManifest,
        "Archive manifest tracking true counts, quotas, rights, and gap analysis",
    ),
}


def export_model_schema(
    model_cls: Type[BaseModel],
    description: str,
    output_path: Path,
) -> dict:
    """Generate and write a JSON Schema Draft 2020-12 document from a Pydantic model."""
    schema = model_cls.model_json_schema(mode="validation")

    # Inject standard Draft 2020-12 schema identifier and metadata
    schema["$schema"] = DRAFT_2020_12_URI
    if description and "description" not in schema:
        schema["description"] = description

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, sort_keys=True)

    return schema


def export_all_schemas(output_dir: Path = Path("data/schemas")) -> list[Path]:
    """Export all required KathaYantra Pydantic models to JSON Schema files."""
    exported_paths: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, (model_cls, desc) in MODELS_TO_EXPORT.items():
        dest = output_dir / filename
        export_model_schema(model_cls, desc, dest)
        exported_paths.append(dest)

    return exported_paths


if __name__ == "__main__":
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/schemas")
    print(f"Exporting JSON Schemas (Draft 2020-12) to: {target_dir}")
    paths = export_all_schemas(target_dir)
    print(f"Successfully exported {len(paths)} JSON Schemas:")
    for p in paths:
        print(f"  - {p.as_posix()}")
