"""Unified Story Endpoints, Sources, and Related Narratives for KathaYantra."""

from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import RelatedStoryItem, SingleResponse
from app.schemas.source import StorySource
from app.schemas.story import StoryRecord

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.get(
    "/{story_id}",
    response_model=SingleResponse[StoryRecord],
    status_code=status.HTTP_200_OK,
    summary="Get Story Record (Unified)",
)
async def get_story_unified(
    story_id: str,
) -> SingleResponse[StoryRecord]:
    """Resolve an approved story record regardless of whether it is folklore or an urban legend."""
    story = story_repository.get_story(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STORY_NOT_FOUND",
                "message": f"Story record '{story_id.upper()}' was not found in the verified archive.",
            },
        )
    return SingleResponse(data=story)


@router.get(
    "/{story_id}/sources",
    response_model=SingleResponse[list[StorySource]],
    status_code=status.HTTP_200_OK,
    summary="Get Documented Bibliographic Sources for a Story",
)
async def get_story_sources(
    story_id: str,
) -> SingleResponse[list[StorySource]]:
    """Retrieve verified historical, archival, or media bibliographic citations supporting this story."""
    story = story_repository.get_story(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STORY_NOT_FOUND",
                "message": f"Story record '{story_id.upper()}' was not found in the verified archive.",
            },
        )
    return SingleResponse(data=story.sources)


@router.get(
    "/{story_id}/related",
    response_model=SingleResponse[list[RelatedStoryItem]],
    status_code=status.HTTP_200_OK,
    summary="Discover Curated and Motif-Related Stories",
)
async def get_related_stories(
    story_id: str,
    limit: int = Query(default=5, ge=1, le=20, description="Maximum related stories to return"),
) -> SingleResponse[list[RelatedStoryItem]]:
    """Discover related narratives based on curated cross-references, shared folkloric motifs, or thematic links."""
    story = story_repository.get_story(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "STORY_NOT_FOUND",
                "message": f"Story record '{story_id.upper()}' was not found in the verified archive.",
            },
        )

    related = story_repository.get_related_stories(story_id, limit=limit)
    return SingleResponse(data=related)
