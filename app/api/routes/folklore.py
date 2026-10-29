"""Folklore Collection Endpoints for KathaYantra."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import PaginatedResponse, PaginationMeta, SingleResponse
from app.schemas.story import CategoryEnum, StoryRecord

router = APIRouter(prefix="/folklore", tags=["Folklore"])


@router.get(
    "",
    response_model=PaginatedResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="List and Filter Authentic Folklore Records",
)
async def list_folklore(
    country_code: Optional[str] = Query(default=None, min_length=2, max_length=2, description="Two-letter ISO country code"),
    region: Optional[str] = Query(default=None, description="Regional or cultural community label"),
    language: Optional[str] = Query(default=None, description="Primary or traditional telling language code"),
    motif: Optional[str] = Query(default=None, description="Thompson motif index identifier or keyword"),
    theme: Optional[str] = Query(default=None, description="Curatorial theme keyword"),
    q: Optional[str] = Query(default=None, min_length=1, max_length=200, description="Search query string"),
    sort_by: str = Query(default="id", pattern="^(id|title|country_code|created_at)$", description="Sort attribute"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="Sort direction"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Starting offset index"),
) -> PaginatedResponse[StoryRecord]:
    """Retrieve verified traditional folklore narratives, myths, and oral tales with filtering and pagination."""
    records, total = story_repository.list_stories(
        category=CategoryEnum.FOLKLORE.value,
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
            "category": CategoryEnum.FOLKLORE.value,
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
    summary="Get Folklore Story Detail",
)
async def get_folklore_story(
    story_id: str,
) -> SingleResponse[StoryRecord]:
    """Retrieve full detail for a verified traditional folklore record."""
    story = story_repository.get_story(story_id)
    if not story or story.category != CategoryEnum.FOLKLORE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STORY_NOT_FOUND",
                "message": f"Folklore record '{story_id.upper()}' was not found in the verified archive.",
            },
        )
    return SingleResponse(data=story)
