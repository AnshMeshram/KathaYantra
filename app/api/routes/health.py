"""Health Check and System Readiness Endpoint for KathaYantra."""

from fastapi import APIRouter, status
import httpx
from app.core.config import settings
from app.services.manifest_service import manifest_service

router = APIRouter(tags=["System"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def get_health_status() -> dict:
    """Return backend health, dataset availability, and local AI runtime state.

    Does NOT fail or crash when Ollama is offline; honestly reports local AI availability.
    """
    # Check dataset files availability
    countries_file = settings.SEED_DIR / "countries.json"
    source_registry_file = settings.SEED_DIR / "source_registry.json"
    raw_csv_file = settings.RAW_DIR / "folk_tales_deduplicated.csv"
    manifest_file = settings.MANIFESTS_DIR / "dataset_manifest.json"
    nation_mapping_file = settings.MANIFESTS_DIR / "nation_mapping_review.json"
    audit_file = settings.MANIFESTS_DIR / "folk_tales_csv_audit.json"

    datasets_status = {
        "countries_json": countries_file.exists(),
        "source_registry_json": source_registry_file.exists(),
        "folklore_seed_dir": settings.folklore_seed_dir.exists(),
        "urban_legends_seed_dir": settings.urban_legends_seed_dir.exists(),
        "raw_csv": raw_csv_file.exists(),
        "manifest_json": manifest_file.exists(),
        "nation_mapping_json": nation_mapping_file.exists(),
        "audit_json": audit_file.exists(),
    }

    # Retrieve real counts from manifest service
    try:
        manifest = manifest_service.compute_manifest()
        actual_total = manifest.current_actual_counts.total_records
        required_total = manifest.required_record_count
        countries_count = len(manifest.country_list)
    except Exception:
        actual_total = 0
        required_total = settings.REQUIRED_TOTAL_RECORDS
        countries_count = settings.TARGET_COUNTRIES_COUNT

    # Safe inspect of Ollama daemon without blocking
    ollama_online = False
    ollama_details = {
        "configured_model": settings.OLLAMA_MODEL,
        "base_url": settings.OLLAMA_BASE_URL,
        "ollama_available": False,
        "note": "Local-first AI runner; Ollama is optional for browsing and data validation."
    }

    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/version")
            if resp.status_code == 200:
                ollama_online = True
                ollama_details["ollama_available"] = True
                ollama_details["version"] = resp.json().get("version", "unknown")
    except Exception:
        # Expected when Ollama daemon is not running
        pass

    # Overall system status
    critical_files_ok = (
        datasets_status["countries_json"]
        and datasets_status["source_registry_json"]
        and datasets_status["folklore_seed_dir"]
        and datasets_status["urban_legends_seed_dir"]
    )
    overall_status = "ok" if critical_files_ok else "degraded"

    return {
        "status": overall_status,
        "app_name": settings.PROJECT_NAME,
        "app_version": settings.PROJECT_VERSION,
        "config_loaded": True,
        "datasets_available": datasets_status,
        "counts": {
            "target_countries": countries_count,
            "actual_total_stories": actual_total,
            "required_total_stories": required_total,
            "target_per_country_folklore": settings.TARGET_FOLKLORE_PER_COUNTRY,
            "target_per_country_urban_legends": settings.TARGET_URBAN_LEGENDS_PER_COUNTRY,
        },
        "local_ai": ollama_details,
    }


@router.get("/health/ollama", status_code=status.HTTP_200_OK, summary="Inspect Ollama AI Model Readiness")
async def get_ollama_status() -> dict:
    """Return local Ollama health and configured model availability without failing whole backend."""
    from app.services.ollama_client import ollama_client

    health = await ollama_client.check_health()
    return health.model_dump(mode="json")


