"""Urban Legends Collection Endpoints for KathaYantra."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import PaginatedResponse, PaginationMeta, SingleResponse
from app.schemas.story import CategoryEnum, StoryRecord

router = APIRouter(prefix="/urban-legends", tags=["Urban Legends"])


@router.get(
    "",
    response_model=PaginatedResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="List and Filter Documented Urban Legends",
)
async def list_urban_legends(
    country_code: Optional[str] = Query(default=None, min_length=2, max_length=2, description="Two-letter ISO country code"),
    region: Optional[str] = Query(default=None, description="Regional or municipal label"),
    language: Optional[str] = Query(default=None, description="Language code"),
    motif: Optional[str] = Query(default=None, description="Urban legend motif identifier or tag"),
    theme: Optional[str] = Query(default=None, description="Thematic tag"),
    q: Optional[str] = Query(default=None, min_length=1, max_length=200, description="Search query string"),
    sort_by: str = Query(default="id", pattern="^(id|title|country_code|created_at)$", description="Sort attribute"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="Sort direction"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Starting offset index"),
) -> PaginatedResponse[StoryRecord]:
    """Retrieve documented contemporary legends, haunted sites, and modern rumors with citations."""
    records, total = story_repository.list_stories(
        category=CategoryEnum.URBAN_LEGEND.value,
        country_code=country_code,
        region=region,
        language=language,
        motif=motif,
        theme=theme,
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
            "category": CategoryEnum.URBAN_LEGEND.value,
            "country_filter": country_code.upper() if country_code else None,
            "region_filter": region,
            "motif_filter": motif,
            "theme_filter": theme,
        },
    )


@router.get(
    "/{story_id}",
    response_model=SingleResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="Get Urban Legend Detail",
)
async def get_urban_legend_story(
    story_id: str,
) -> SingleResponse[StoryRecord]:
    """Retrieve full detail for a verified modern urban legend record."""
    story = story_repository.get_story(story_id)
    if not story or story.category != CategoryEnum.URBAN_LEGEND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STORY_NOT_FOUND",
                "message": f"Urban legend record '{story_id.upper()}' was not found in the verified archive.",
            },
        )
    return SingleResponse(data=story)
