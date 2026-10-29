"""Source Registry and Provenance Directory Endpoints for KathaYantra."""

from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.story_repository import story_repository
from app.schemas.api import PaginatedResponse, PaginationMeta, SingleResponse

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get(
    "",
    response_model=PaginatedResponse[dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Registered External Sources and APIs",
)
async def list_sources(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Starting offset index"),
) -> PaginatedResponse[dict[str, Any]]:
    """Retrieve catalog of 17 registered external archives, national libraries, and open-data APIs."""
    sources = story_repository.list_sources()

    # Sanitization: Ensure no sensitive fields or keys are ever returned
    sanitized_sources = []
    for s in sources:
        clean = {k: v for k, v in s.items() if not k.lower().endswith("key") and not k.lower().endswith("secret")}
        sanitized_sources.append(clean)

    total = len(sanitized_sources)
    start = max(0, offset)
    end = start + limit
    paged = sanitized_sources[start:end]

    return PaginatedResponse(
        data=paged,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=end < total,
            has_prev=offset > 0,
        ),
        meta={"total_sources": total},
    )


@router.get(
    "/{source_id}",
    response_model=SingleResponse[dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Source Registry Item Detail",
)
async def get_source(
    source_id: str,
) -> SingleResponse[dict[str, Any]]:
    """Retrieve metadata, rights assessment, and integration status for a specific source registry entry."""
    source = story_repository.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "SOURCE_NOT_FOUND",
                "message": f"Source registry entry '{source_id}' was not found.",
            },
        )

    # Sanitize
    clean = {k: v for k, v in source.items() if not k.lower().endswith("key") and not k.lower().endswith("secret")}
    return SingleResponse(data=clean)
