"""Search and Autocomplete Endpoints for KathaYantra Archive."""

from typing import Optional
from fastapi import APIRouter, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import PaginatedResponse, PaginationMeta, SearchSuggestion, SingleResponse
from app.schemas.story import CategoryEnum, StoryRecord

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=PaginatedResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="Search KathaYantra Folklore and Urban Legend Catalog",
)
async def search_archive(
    q: str = Query(min_length=1, max_length=200, description="Search query string"),
    category: Optional[CategoryEnum] = Query(default=None, description="Filter by category ('folklore' or 'urban_legend')"),
    country_code: Optional[str] = Query(default=None, min_length=2, max_length=2, description="Two-letter ISO country code"),
    language: Optional[str] = Query(default=None, description="Language code"),
    motif: Optional[str] = Query(default=None, description="Thompson motif index identifier or tag"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page (max 50)"),
    offset: int = Query(default=0, ge=0, description="Starting offset index"),
) -> PaginatedResponse[StoryRecord]:
    """Execute high-precision lexical catalog search over titles, alternate names, motifs, and summaries."""
    records, total = story_repository.search(
        query=q,
        category=category.value if category else None,
        country_code=country_code,
        language=language,
        motif=motif,
        limit=limit,
        offset=offset,
    )

    return PaginatedResponse(
        data=records,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=(offset + limit) < total,
            has_prev=offset > 0,
        ),
        meta={
            "query": q,
            "category_filter": category.value if category else None,
            "country_filter": country_code.upper() if country_code else None,
            "language_filter": language,
            "motif_filter": motif,
        },
    )


@router.get(
    "/suggest",
    response_model=SingleResponse[list[SearchSuggestion]],
    status_code=status.HTTP_200_OK,
    summary="Get Search Autocomplete Suggestions",
)
async def get_search_suggestions(
    q: str = Query(min_length=2, max_length=100, description="Prefix or partial query string"),
    limit: int = Query(default=10, ge=1, le=20, description="Maximum suggestions to return"),
) -> SingleResponse[list[SearchSuggestion]]:
    """Generate bounded, informative search suggestions matching story titles, alternate names, motifs, or regions."""
    suggestions = story_repository.suggest(query=q, limit=limit)
    return SingleResponse(data=suggestions)
