"""KathaYantra API Routes Package."""

from app.api.routes.ai import router as ai_router
from app.api.routes.countries import router as countries_router
from app.api.routes.dataset import router as dataset_router
from app.api.routes.folklore import router as folklore_router
from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.sources import router as sources_router
from app.api.routes.stories import router as stories_router
from app.api.routes.urban_legends import router as urban_legends_router

__all__ = [
    "ai_router",
    "countries_router",
    "dataset_router",
    "folklore_router",
    "health_router",
    "search_router",
    "sources_router",
    "stories_router",
    "urban_legends_router",
]
