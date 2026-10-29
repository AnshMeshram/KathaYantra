"""Deterministic Lexical Retrieval Service for KathaYantra Using SQLite FTS5.

Executes ranked BM25 search queries over verified story records with schema-level
safeguards, country/category filters, and citation reconstruction.
"""

import json
import logging
import re
import sqlite3
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.source import RightsStatusEnum, StorySource
from app.schemas.story import CategoryEnum, VerificationStatusEnum
from app.services.retrieval_index import RetrievalIndexService, retrieval_index_service

logger = logging.getLogger(__name__)


class RetrievalResultItem(BaseModel):
    """An individual ranked search result from the retrieval index."""

    story_id: str
    title: str
    country_code: str
    category: CategoryEnum
    score: float = Field(..., description="Normalized positive relevance score (higher = more relevant)")
    match_reason: str = Field(default="keyword_match", description="Explanation of why this record matched")
    summary: str
    sources: list[StorySource] = Field(default_factory=list)
    verification_status: VerificationStatusEnum
    rights_status: RightsStatusEnum
    attribution_text: Optional[str] = None
    cultural_community: Optional[str] = None
    region: Optional[str] = None
    motifs: list[str] = Field(default_factory=list)
    dataset_path: Optional[str] = None

    @property
    def id(self) -> str:
        """Alias for story_id for convenience."""
        return self.story_id


class RetrievalService:
    """Performs deterministic, lexical BM25 search queries against the local FTS5 index."""

    STOPWORDS = {
        "a", "an", "the", "and", "or", "of", "in", "to", "for", "with",
        "on", "at", "from", "by", "about", "as", "into", "through", "during",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "can", "could", "should", "would",
        "may", "might", "must", "will", "shall", "tell", "me", "what",
        "who", "where", "when", "why", "how", "which", "there", "this",
        "that", "these", "those", "it", "its", "i", "you", "he", "she",
        "we", "they", "them", "their", "his", "her", "my", "your",
    }

    def __init__(self, index_service: Optional[RetrievalIndexService] = None):
        self.index_service = index_service or retrieval_index_service

    def _sanitize_fts_query(self, raw_query: str) -> str:
        """Sanitize raw user query into safe, effective FTS5 search terms."""
        # Remove characters that can break SQLite FTS5 syntax
        cleaned = re.sub(r"[^\w\s]", " ", raw_query)
        all_tokens = [t.strip().lower() for t in cleaned.split() if len(t.strip()) >= 2]
        content_tokens = [t for t in all_tokens if t not in self.STOPWORDS]
        tokens = content_tokens if content_tokens else all_tokens
        if not tokens:
            return ""

        # Form prefix search tokens (e.g. "betal* OR pachisi*")
        terms = [f'"{tok}"*' for tok in tokens]
        return " OR ".join(terms)

    def search(
        self,
        query: str,
        country_code: Optional[str] = None,
        category: Optional[CategoryEnum] = None,
        limit: int = 5,
        min_score: Optional[float] = None,
    ) -> list[RetrievalResultItem]:
        """Execute a ranked lexical BM25 search over the verified stories index."""
        if not self.index_service.db_path.exists():
            # If index not yet built, build it now
            logger.info("Retrieval index not found. Building index automatically...")
            self.index_service.rebuild_index()

        sanitized_fts = self._sanitize_fts_query(query)
        if not sanitized_fts:
            return []

        con = self.index_service.get_connection()
        results: list[RetrievalResultItem] = []
        target_min_score = min_score if min_score is not None else settings.AI_RETRIEVAL_MIN_SCORE

        try:
            # Build query with optional filters
            sql = """
            SELECT
                id, country_code, category, title, alternate_names,
                summary, motifs, themes, cultural_community, region,
                sources_json, attribution_text, verification_status,
                rights_status, dataset_path,
                bm25(stories_fts, 5.0, 2.0, 1.0, 1.5, 1.0, 2.0, 1.0) as bm25_rank
            FROM stories_fts
            WHERE stories_fts MATCH ?
            """
            params: list[Any] = [sanitized_fts]

            if country_code:
                sql += " AND country_code = ?"
                params.append(country_code.upper().strip())

            if category:
                cat_val = category.value if isinstance(category, CategoryEnum) else str(category)
                sql += " AND category = ?"
                params.append(cat_val)

            sql += " ORDER BY bm25_rank ASC LIMIT ?"
            params.append(max(1, limit * 2))  # Fetch extra candidates for score threshold filtering

            cursor = con.execute(sql, params)
            rows = cursor.fetchall()

            for r in rows:
                raw_bm25 = float(r["bm25_rank"])
                # In FTS5, lower (more negative) raw BM25 values indicate stronger matches.
                # Convert to positive normalized score where higher is better.
                norm_score = round(10.0 / (1.0 + max(0.0, raw_bm25 + 15.0)), 3)

                if norm_score < target_min_score:
                    continue

                sources_data = json.loads(r["sources_json"]) if r["sources_json"] else []
                sources = [StorySource.model_validate(s) for s in sources_data]

                motifs_list = [m for m in (r["motifs"] or "").split() if m]
                cat_enum = CategoryEnum(r["category"])

                reason = f"Matched search terms in {r['category']} archive (BM25: {raw_bm25:.2f})"

                results.append(
                    RetrievalResultItem(
                        story_id=r["id"],
                        title=r["title"],
                        country_code=r["country_code"],
                        category=cat_enum,
                        score=norm_score,
                        match_reason=reason,
                        summary=r["summary"],
                        sources=sources,
                        verification_status=VerificationStatusEnum(r["verification_status"]),
                        rights_status=RightsStatusEnum(r["rights_status"]),
                        attribution_text=r["attribution_text"],
                        cultural_community=r["cultural_community"],
                        region=r["region"],
                        motifs=motifs_list,
                        dataset_path=r["dataset_path"],
                    )
                )

                if len(results) >= limit:
                    break

        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 query failed for '{sanitized_fts}': {e}. Falling back to LIKE search.")
            results = self._fallback_like_search(con, query, country_code, category, limit)
        finally:
            con.close()

        return results

    def _fallback_like_search(
        self,
        con: sqlite3.Connection,
        raw_query: str,
        country_code: Optional[str],
        category: Optional[CategoryEnum],
        limit: int,
    ) -> list[RetrievalResultItem]:
        """Fallback simple substring match when FTS5 syntax encounters an unexpected query."""
        tokens = [t.strip().lower() for t in raw_query.split() if len(t.strip()) >= 3]
        if not tokens:
            return []

        sql = """
        SELECT
            id, country_code, category, title, alternate_names,
            summary, motifs, themes, cultural_community, region,
            sources_json, attribution_text, verification_status,
            rights_status, dataset_path
        FROM stories_fts
        WHERE (title LIKE ? OR summary LIKE ? OR alternate_names LIKE ? OR cultural_community LIKE ?)
        """
        pattern = f"%{tokens[0]}%"
        params: list[Any] = [pattern, pattern, pattern, pattern]

        if country_code:
            sql += " AND country_code = ?"
            params.append(country_code.upper().strip())

        if category:
            cat_val = category.value if isinstance(category, CategoryEnum) else str(category)
            sql += " AND category = ?"
            params.append(cat_val)

        sql += " LIMIT ?"
        params.append(limit)

        rows = con.execute(sql, params).fetchall()
        results: list[RetrievalResultItem] = []
        for r in rows:
            sources_data = json.loads(r["sources_json"]) if r["sources_json"] else []
            sources = [StorySource.model_validate(s) for s in sources_data]
            results.append(
                RetrievalResultItem(
                    story_id=r["id"],
                    title=r["title"],
                    country_code=r["country_code"],
                    category=CategoryEnum(r["category"]),
                    score=0.6,
                    match_reason="Fallback substring match",
                    summary=r["summary"],
                    sources=sources,
                    verification_status=VerificationStatusEnum(r["verification_status"]),
                    rights_status=RightsStatusEnum(r["rights_status"]),
                    attribution_text=r["attribution_text"],
                    cultural_community=r["cultural_community"],
                    region=r["region"],
                    motifs=[m for m in (r["motifs"] or "").split() if m],
                    dataset_path=r["dataset_path"],
                )
            )
        return results

    def get_by_id(self, story_id: str) -> Optional[RetrievalResultItem]:
        """Fetch an individual indexed record by canonical story ID."""
        records = self.get_multiple_by_ids([story_id])
        return records[0] if records else None

    def get_multiple_by_ids(self, story_ids: list[str]) -> list[RetrievalResultItem]:
        """Retrieve a specific batch of indexed records by their canonical story IDs."""
        if not story_ids:
            return []

        if not self.index_service.db_path.exists():
            self.index_service.rebuild_index()

        con = self.index_service.get_connection()
        clean_ids = [sid.strip().upper() for sid in story_ids if sid and sid.strip()]
        placeholders = ",".join("?" for _ in clean_ids)

        sql = f"""
        SELECT
            id, country_code, category, title, alternate_names,
            summary, motifs, themes, cultural_community, region,
            sources_json, attribution_text, verification_status,
            rights_status, dataset_path
        FROM stories_fts
        WHERE id IN ({placeholders})
        """

        try:
            rows = con.execute(sql, clean_ids).fetchall()
            results: list[RetrievalResultItem] = []
            for r in rows:
                sources_data = json.loads(r["sources_json"]) if r["sources_json"] else []
                sources = [StorySource.model_validate(s) for s in sources_data]
                results.append(
                    RetrievalResultItem(
                        story_id=r["id"],
                        title=r["title"],
                        country_code=r["country_code"],
                        category=CategoryEnum(r["category"]),
                        score=1.0,
                        match_reason="Exact story ID lookup",
                        summary=r["summary"],
                        sources=sources,
                        verification_status=VerificationStatusEnum(r["verification_status"]),
                        rights_status=RightsStatusEnum(r["rights_status"]),
                        attribution_text=r["attribution_text"],
                        cultural_community=r["cultural_community"],
                        region=r["region"],
                        motifs=[m for m in (r["motifs"] or "").split() if m],
                        dataset_path=r["dataset_path"],
                    )
                )
            return results
        finally:
            con.close()


# Central singleton instance
retrieval_service = RetrievalService()
