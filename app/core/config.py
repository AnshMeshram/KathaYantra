"""KathaYantra Core Configuration Module.

Loads environment variables, validates settings via Pydantic v2 Settings,
and defines central application parameters and directory paths.
"""

from pathlib import Path
from typing import Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    PROJECT_NAME: str = Field(default="KathaYantra", description="Application name")
    PROJECT_VERSION: str = Field(default="0.3.0", description="Application version")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API route prefix")
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Allowed CORS Origins for local development
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        description="Allowed CORS origins",
    )

    # Local AI Engine (Ollama + Gemma 2)
    OLLAMA_BASE_URL: str = Field(
        default="http://127.0.0.1:11434",
        description="Ollama local server endpoint",
    )
    OLLAMA_MODEL: str = Field(
        default="gemma2",
        description="Configured model tag (e.g. gemma2, gemma2:9b)",
    )
    OLLAMA_TIMEOUT_SECONDS: float = Field(
        default=60.0,
        description="Timeout for local AI generation requests",
    )

    # External API Keys (stored in environment, never committed)
    EUROPEANA_API_KEY: str = Field(default="", description="Optional Europeana API key")
    JAPAN_SEARCH_API_KEY: str = Field(default="", description="Optional Japan Search key")

    # HTTP Client Configuration & Safe Scraping Controls
    KATHAYANTRA_USER_AGENT: str = Field(
        default="KathaYantra/0.3.0 (https://github.com/AnshMeshram/KathaYantra; mailto:dev@rmsc.org)",
        description="User-Agent header sent to upstream open-data APIs",
    )
    HTTP_TIMEOUT_SECONDS: float = Field(default=30.0, description="HTTP client overall timeout")
    HTTP_CONNECT_TIMEOUT: float = Field(default=10.0, description="HTTP connect timeout in seconds")
    HTTP_READ_TIMEOUT: float = Field(default=30.0, description="HTTP read timeout in seconds")
    HTTP_MAX_RETRIES: int = Field(default=3, description="HTTP retry limit for transient errors")
    HTTP_MAX_CONCURRENCY: int = Field(default=5, description="Max concurrent outgoing requests")
    HTTP_CACHE_TTL_SECONDS: int = Field(default=86400, description="HTTP response cache TTL in seconds")
    MAX_RESPONSE_SIZE_BYTES: int = Field(default=50 * 1024 * 1024, description="Max upstream response size (50MB)")

    # Data Ingestion and Candidate Pipeline
    IMPORT_MAX_RESULTS: int = Field(default=50, description="Default max results per import query")
    IMPORT_OUTPUT_DIR: Path = Field(
        default=BASE_DIR / "data" / "processed" / "candidates",
        description="Staged import candidate storage path",
    )

    # Data Directories
    DATA_DIR: Path = Field(default=BASE_DIR / "data", description="Data directory path")
    SEED_DIR: Path = Field(default=BASE_DIR / "data" / "seed", description="Seed directory")
    RAW_DIR: Path = Field(default=BASE_DIR / "data" / "raw", description="Raw data directory")
    PROCESSED_DIR: Path = Field(
        default=BASE_DIR / "data" / "processed",
        description="Processed staging directory",
    )
    MANIFESTS_DIR: Path = Field(
        default=BASE_DIR / "data" / "manifests",
        description="Manifests directory",
    )

    # Target Dataset Quotas
    TARGET_COUNTRIES_COUNT: int = 15
    TARGET_FOLKLORE_PER_COUNTRY: int = 10
    TARGET_URBAN_LEGENDS_PER_COUNTRY: int = 10
    REQUIRED_TOTAL_RECORDS: int = 300  # 15 * (10 + 10)

    # Data Safeguards
    MAX_IMPORT_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            import json

            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def folklore_seed_dir(self) -> Path:
        return self.SEED_DIR / "folklore"

    @property
    def urban_legends_seed_dir(self) -> Path:
        return self.SEED_DIR / "urban_legends"

    @property
    def candidates_dir(self) -> Path:
        return self.IMPORT_OUTPUT_DIR


# Central settings instance
settings = Settings()

