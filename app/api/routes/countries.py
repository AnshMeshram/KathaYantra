"""Country Registry and Statistical Endpoints for KathaYantra."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import (
    CountryStatsResponse,
    PaginatedResponse,
    PaginationMeta,
    SingleResponse,
)
from app.schemas.country import CountryRecord
from app.schemas.story import CategoryEnum, StoryRecord

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get(
    "",
    response_model=PaginatedResponse[CountryRecord],
    status_code=status.HTTP_200_OK,
    summary="List Supported Target Countries",
)
async def list_countries(
    limit: int = Query(default=20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(default=0, ge=0, description="Offset index"),
) -> PaginatedResponse[CountryRecord]:
    """Retrieve canonical list of all supported target countries with folkloric metadata."""
    countries = story_repository.list_countries()
    total = len(countries)
    start = max(0, offset)
    end = start + limit
    paged = countries[start:end]

    return PaginatedResponse(
        data=paged,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=end < total,
            has_prev=offset > 0,
        ),
        meta={"total_countries": total},
    )


@router.get(
    "/{country_code}",
    response_model=SingleResponse[CountryRecord],
    status_code=status.HTTP_200_OK,
    summary="Get Country Details",
)
async def get_country(
    country_code: str,
) -> SingleResponse[CountryRecord]:
    """Retrieve a single country record by its ISO 3166-1 alpha-2 code."""
    country = story_repository.get_country(country_code)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "COUNTRY_NOT_FOUND",
                "message": f"Country '{country_code.upper()}' is not a registered target country.",
            },
        )
    return SingleResponse(data=country)


@router.get(
    "/{country_code}/stats",
    response_model=SingleResponse[CountryStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Country Archive Statistics and Quotas",
)
async def get_country_stats(
    country_code: str,
) -> SingleResponse[CountryStatsResponse]:
    """Calculate actual published folklore and urban-legend records, targets, and deficits for a country."""
    stats = story_repository.get_country_stats(country_code)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "COUNTRY_NOT_FOUND",
                "message": f"Country '{country_code.upper()}' is not a registered target country.",
            },
        )
    return SingleResponse(data=stats)


@router.get(
    "/{country_code}/stories",
    response_model=PaginatedResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="Browse Stories by Country",
)
async def list_country_stories(
    country_code: str,
    category: Optional[CategoryEnum] = Query(default=None, description="Filter by category ('folklore' or 'urban_legend')"),
    language: Optional[str] = Query(default=None, description="Filter by primary or alternate language code"),
    motif: Optional[str] = Query(default=None, description="Filter by Thompson motif code or keyword"),
    q: Optional[str] = Query(default=None, min_length=1, max_length=200, description="Substring search query"),
    sort_by: str = Query(default="id", pattern="^(id|title|created_at)$", description="Field to sort by"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="Sort direction"),
    limit: int = Query(default=10, ge=1, le=100, description="Page size limit"),
    offset: int = Query(default=0, ge=0, description="Page starting offset"),
) -> PaginatedResponse[StoryRecord]:
    """Retrieve published stories originating from a specific country with optional filters."""
    country = story_repository.get_country(country_code)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "COUNTRY_NOT_FOUND",
                "message": f"Country '{country_code.upper()}' is not a registered target country.",
            },
        )

    records, total = story_repository.list_stories(
        category=category.value if category else None,
        country_code=country_code,
        language=language,
        motif=motif,
        search_query=q,
        sort_by=sort_by,
        sort_order=sort_order,
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
            "country_code": country_code.upper(),
            "category": category.value if category else "all",
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
    )
