"""Story, Country, and Source Memory-Cached Repository for KathaYantra."""

from collections import Counter, defaultdict
import json
import logging
from pathlib import Path
import re
from typing import Any, Optional
from app.core.config import settings
from app.schemas.api import CountryStatsResponse, RelatedStoryItem, SearchSuggestion
from app.schemas.country import CountryRecord
from app.schemas.dataset import DatasetEnvelope
from app.schemas.source import StorySource
from app.schemas.story import CategoryEnum, ContentOriginEnum, StoryRecord, VerificationStatusEnum
from app.services.publication_policy import PublicationPolicy

logger = logging.getLogger("kathayantra.repository")


class StoryRepository:
    """High-performance, in-memory repository serving validated folklore and urban-legend records."""

    def __init__(self):
        self._stories: dict[str, StoryRecord] = {}
        self._countries: dict[str, CountryRecord] = {}
        self._sources: list[dict[str, Any]] = []
        self._sources_by_id: dict[str, dict[str, Any]] = {}
        self._stories_by_country: dict[str, list[StoryRecord]] = defaultdict(list)
        self._stories_by_category: dict[str, list[StoryRecord]] = defaultdict(list)
        self._motifs_index: dict[str, set[str]] = defaultdict(set)
        self._themes_index: dict[str, set[str]] = defaultdict(set)
        self._loaded: bool = False

    def load(self, force_reload: bool = False) -> None:
        """Load and cache canonical seed records in memory."""
        if self._loaded and not force_reload:
            return

        stories: dict[str, StoryRecord] = {}
        countries: dict[str, CountryRecord] = {}
        sources: list[dict[str, Any]] = []
        sources_by_id: dict[str, dict[str, Any]] = {}
        by_country: dict[str, list[StoryRecord]] = defaultdict(list)
        by_category: dict[str, list[StoryRecord]] = defaultdict(list)
        motifs_idx: dict[str, set[str]] = defaultdict(set)
        themes_idx: dict[str, set[str]] = defaultdict(set)

        # 1. Load Countries
        countries_file = settings.SEED_DIR / "countries.json"
        if countries_file.exists():
            try:
                with open(countries_file, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                for item in c_data:
                    c_rec = CountryRecord.model_validate(item)
                    countries[c_rec.code.upper()] = c_rec
            except Exception as e:
                logger.error("Failed loading countries.json: %s", e)

        # 2. Load Sources
        sources_file = settings.SEED_DIR / "source_registry.json"
        if sources_file.exists():
            try:
                with open(sources_file, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                for item in s_data:
                    sources.append(item)
                    s_id = item.get("id")
                    if s_id:
                        sources_by_id[s_id] = item
            except Exception as e:
                logger.error("Failed loading source_registry.json: %s", e)

        # 3. Load 30 Seed Files
        folklore_dir = settings.folklore_seed_dir
        urban_dir = settings.urban_legends_seed_dir

        for country_code in sorted(countries.keys()):
            for c_dir, cat_val in [(folklore_dir, "folklore"), (urban_dir, "urban_legend")]:
                seed_file = c_dir / f"{country_code}.json"
                if not seed_file.exists():
                    continue

                try:
                    with open(seed_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    envelope = DatasetEnvelope.model_validate(data)

                    for story in envelope.records:
                        # Archival safeguard: verify eligibility
                        if story.content_origin == ContentOriginEnum.AI_GENERATED_FICTION:
                            continue
                        if story.verification_status != VerificationStatusEnum.VERIFIED:
                            continue

                        eval_result = PublicationPolicy.evaluate_eligibility(story)
                        if not eval_result.is_eligible:
                            logger.warning("Excluding ineligible story %s: %s", story.id, eval_result.violations)
                            continue

                        stories[story.id] = story
                        by_country[story.country_code.upper()].append(story)
                        by_category[story.category.value].append(story)

                        for m in story.motifs:
                            motifs_idx[m.lower()].add(story.id)
                        for t in story.themes:
                            themes_idx[t.lower()].add(story.id)

                except Exception as e:
                    logger.error("Error loading seed file %s: %s", seed_file, e)

        # Atomic swap
        self._stories = stories
        self._countries = countries
        self._sources = sources
        self._sources_by_id = sources_by_id
        self._stories_by_country = by_country
        self._stories_by_category = by_category
        self._motifs_index = motifs_idx
        self._themes_index = themes_idx
        self._loaded = True

        logger.info(
            "StoryRepository loaded %d stories across %d countries (%d sources)",
            len(self._stories),
            len(self._countries),
            len(self._sources),
        )

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # --- Country Queries ---

    def list_countries(self) -> list[CountryRecord]:
        """List all canonical country records ordered by country code."""
        self._ensure_loaded()
        return [self._countries[code] for code in sorted(self._countries.keys())]

    def get_country(self, country_code: str) -> Optional[CountryRecord]:
        """Retrieve a specific country record by ISO alpha-2 code."""
        self._ensure_loaded()
        return self._countries.get(country_code.upper())

    def get_country_stats(self, country_code: str) -> Optional[CountryStatsResponse]:
        """Compute real-time published story counts, targets, and deficits for a country."""
        self._ensure_loaded()
        code = country_code.upper()
        country = self._countries.get(code)
        if not country:
            return None

        country_stories = self._stories_by_country.get(code, [])
        folklore_count = sum(1 for s in country_stories if s.category == CategoryEnum.FOLKLORE)
        urban_count = sum(1 for s in country_stories if s.category == CategoryEnum.URBAN_LEGEND)
        total_count = len(country_stories)

        folklore_target = country.record_targets.folklore if country.record_targets else 10
        urban_target = country.record_targets.urban_legends if country.record_targets else 10
        total_target = folklore_target + urban_target

        folklore_gap = max(0, folklore_target - folklore_count)
        urban_gap = max(0, urban_target - urban_count)
        total_gap = folklore_gap + urban_gap
        is_quotas_met = folklore_gap == 0 and urban_gap == 0

        # Unique sources count for this country
        seen_urls = set()
        for s in country_stories:
            for src in s.sources:
                if src.url:
                    seen_urls.add(str(src.url))

        return CountryStatsResponse(
            country_code=country.code,
            country_name=country.name,
            folklore_count=folklore_count,
            urban_legend_count=urban_count,
            total_count=total_count,
            folklore_target=folklore_target,
            urban_legend_target=urban_target,
            total_target=total_target,
            folklore_gap=folklore_gap,
            urban_legend_gap=urban_gap,
            total_gap=total_gap,
            is_quotas_met=is_quotas_met,
            source_count=len(seen_urls),
            cultural_context=country.cultural_context,
        )

    # --- Story Queries ---

    def get_story(self, story_id: str) -> Optional[StoryRecord]:
        """Retrieve an authentic story record by its canonical ID."""
        self._ensure_loaded()
        return self._stories.get(story_id.upper())

    def list_stories(
        self,
        category: Optional[str] = None,
        country_code: Optional[str] = None,
        region: Optional[str] = None,
        language: Optional[str] = None,
        motif: Optional[str] = None,
        theme: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[StoryRecord], int]:
        """Filter, sort, and paginate published story records."""
        self._ensure_loaded()

        records = list(self._stories.values())

        # 1. Filter by Category
        if category:
            cat_norm = category.lower()
            records = [r for r in records if r.category.value == cat_norm]

        # 2. Filter by Country Code
        if country_code:
            c_norm = country_code.upper()
            records = [r for r in records if r.country_code.upper() == c_norm]

        # 3. Filter by Region or Community
        if region:
            reg_norm = region.lower()
            records = [
                r for r in records
                if (r.region_or_community and reg_norm in r.region_or_community.lower())
                or any(reg_norm in comm.lower() for comm in r.community_attributions)
            ]

        # 4. Filter by Language
        if language:
            lang_norm = language.lower()
            records = [r for r in records if r.language.lower() == lang_norm or lang_norm in [l.lower() for l in r.alternate_languages]]

        # 5. Filter by Motif
        if motif:
            motif_norm = motif.lower()
            records = [r for r in records if any(motif_norm in m.lower() for m in r.motifs)]

        # 6. Filter by Theme
        if theme:
            theme_norm = theme.lower()
            records = [r for r in records if any(theme_norm in t.lower() for t in r.themes)]

        # 7. Substring Search
        if search_query:
            sq = search_query.lower()
            records = [
                r for r in records
                if sq in r.title.lower()
                or sq in r.summary.lower()
                or any(sq in name.lower() for name in r.alternate_names)
                or any(sq in m.lower() for m in r.motifs)
                or any(sq in t.lower() for t in r.themes)
                or (r.region_or_community and sq in r.region_or_community.lower())
            ]

        total = len(records)

        # 8. Sort
        reverse = sort_order.lower() == "desc"
        if sort_by == "title":
            records.sort(key=lambda r: r.title.lower(), reverse=reverse)
        elif sort_by == "country_code":
            records.sort(key=lambda r: (r.country_code, r.id), reverse=reverse)
        elif sort_by == "created_at":
            records.sort(key=lambda r: r.created_at, reverse=reverse)
        else:
            # Default sort by ID
            records.sort(key=lambda r: r.id, reverse=reverse)

        # 9. Paginate
        start = max(0, offset)
        end = start + max(1, limit)
        paged_records = records[start:end]

        return paged_records, total

    # --- Related Records ---

    def get_related_stories(self, story_id: str, limit: int = 5) -> list[RelatedStoryItem]:
        """Find approved related stories based on explicit references, shared motifs, or themes."""
        self._ensure_loaded()
        target = self.get_story(story_id)
        if not target:
            return []

        candidates: list[dict[str, Any]] = []
        seen_ids = {target.id}

        # 1. Explicit curatorial cross-references
        for rel_id in target.related_record_ids:
            rel_story = self.get_story(rel_id)
            if rel_story and rel_story.id not in seen_ids:
                candidates.append({
                    "story": rel_story,
                    "relationship_basis": "Direct curatorial relationship and shared folklore cycle",
                    "shared_motifs": list(set(target.motifs) & set(rel_story.motifs)),
                    "shared_themes": list(set(target.themes) & set(rel_story.themes)),
                    "score": 100.0,
                })
                seen_ids.add(rel_story.id)

        # 2. Motif & theme sharing
        target_motifs = set(m.lower() for m in target.motifs)
        target_themes = set(t.lower() for t in target.themes)

        for other_id, other in self._stories.items():
            if other_id in seen_ids:
                continue

            other_motifs = set(m.lower() for m in other.motifs)
            other_themes = set(t.lower() for t in other.themes)

            shared_m = target_motifs & other_motifs
            shared_t = target_themes & other_themes

            if not shared_m and not shared_t:
                continue

            score = (len(shared_m) * 3.0) + (len(shared_t) * 1.5)
            if other.country_code == target.country_code:
                score += 1.0

            basis_parts = []
            if shared_m:
                basis_parts.append(f"Shared folkloric motifs ({', '.join(sorted(shared_m))})")
            if shared_t:
                basis_parts.append(f"Shared narrative themes ({', '.join(sorted(shared_t))})")
            basis = "; ".join(basis_parts) if basis_parts else "Thematic affinity"

            candidates.append({
                "story": other,
                "relationship_basis": basis,
                "shared_motifs": [m for m in other.motifs if m.lower() in shared_m],
                "shared_themes": [t for t in other.themes if t.lower() in shared_t],
                "score": score,
            })
            seen_ids.add(other.id)

        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = candidates[:max(1, limit)]

        results = []
        for c in top_candidates:
            st: StoryRecord = c["story"]
            results.append(RelatedStoryItem(
                story_id=st.id,
                title=st.title,
                category=st.category.value,
                country_code=st.country_code,
                summary=st.summary,
                relationship_basis=c["relationship_basis"],
                shared_motifs=c["shared_motifs"],
                shared_themes=c["shared_themes"],
            ))

        return results

    # --- Search & Suggestions ---

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        country_code: Optional[str] = None,
        language: Optional[str] = None,
        motif: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[StoryRecord], int]:
        """Perform search across title, alternate names, summary, motifs, and community labels."""
        self._ensure_loaded()
        q = query.strip().lower()
        if not q:
            return [], 0

        # Try SQLite FTS5 search first if index exists
        try:
            from app.services.retrieval import retrieval_service
            cat_enum = CategoryEnum(category.lower()) if category else None
            fts_results = retrieval_service.search(
                query=query,
                category=cat_enum,
                country=country_code.upper() if country_code else None,
                limit=100,
            )
            if fts_results:
                matched_stories = []
                for res in fts_results:
                    st = self.get_story(res.story_id)
                    if not st:
                        continue
                    if language and st.language.lower() != language.lower():
                        continue
                    if motif and not any(motif.lower() in m.lower() for m in st.motifs):
                        continue
                    matched_stories.append(st)

                total = len(matched_stories)
                start = max(0, offset)
                end = start + max(1, limit)
                return matched_stories[start:end], total
        except Exception as e:
            logger.debug("FTS5 search fallback to in-memory: %s", e)

        # In-Memory Deterministic Fallback Search
        tokens = [t for t in re.split(r"\W+", q) if len(t) > 1]
        scored_stories: list[tuple[float, StoryRecord]] = []

        for st in self._stories.values():
            if category and st.category.value != category.lower():
                continue
            if country_code and st.country_code.upper() != country_code.upper():
                continue
            if language and st.language.lower() != language.lower():
                continue
            if motif and not any(motif.lower() in m.lower() for m in st.motifs):
                continue

            score = 0.0
            st_title = st.title.lower()
            st_summary = st.summary.lower()
            st_alt = " ".join(st.alternate_names).lower()
            st_motifs = " ".join(st.motifs).lower()
            st_themes = " ".join(st.themes).lower()
            st_region = (st.region_or_community or "").lower()

            # Exact phrase match boosts
            if q in st_title:
                score += 50.0
            if q in st_alt:
                score += 30.0
            if q in st_summary:
                score += 20.0
            if q in st_motifs:
                score += 25.0
            if q in st_region:
                score += 15.0

            # Token level matches
            for token in tokens:
                if token in st_title:
                    score += 10.0
                if token in st_alt:
                    score += 6.0
                if token in st_summary:
                    score += 3.0
                if token in st_motifs:
                    score += 5.0
                if token in st_themes:
                    score += 4.0
                if token in st_region:
                    score += 3.0

            if score > 0:
                scored_stories.append((score, st))

        scored_stories.sort(key=lambda x: (x[0], x[1].id), reverse=True)
        total = len(scored_stories)
        start = max(0, offset)
        end = start + max(1, limit)
        paged = [item[1] for item in scored_stories[start:end]]
        return paged, total

    def suggest(self, query: str, limit: int = 10) -> list[SearchSuggestion]:
        """Generate bounded search suggestions from titles, motifs, regions, and alternate names."""
        self._ensure_loaded()
        q = query.strip().lower()
        if not q or len(q) < 2:
            return []

        suggestions: list[SearchSuggestion] = []
        seen = set()

        # Check titles
        for st in self._stories.values():
            if q in st.title.lower():
                key = ("title", st.title)
                if key not in seen:
                    suggestions.append(SearchSuggestion(
                        text=st.title,
                        suggestion_type="title",
                        category=st.category.value,
                        country_code=st.country_code,
                    ))
                    seen.add(key)
                if len(suggestions) >= limit:
                    return suggestions

        # Check alternate names
        for st in self._stories.values():
            for alt in st.alternate_names:
                if q in alt.lower():
                    key = ("alternate_name", alt)
                    if key not in seen:
                        suggestions.append(SearchSuggestion(
                            text=alt,
                            suggestion_type="alternate_name",
                            category=st.category.value,
                            country_code=st.country_code,
                        ))
                        seen.add(key)
                    if len(suggestions) >= limit:
                        return suggestions

        # Check motifs
        for st in self._stories.values():
            for m in st.motifs:
                if q in m.lower():
                    key = ("motif", m)
                    if key not in seen:
                        suggestions.append(SearchSuggestion(
                            text=m,
                            suggestion_type="motif",
                            category=st.category.value,
                        ))
                        seen.add(key)
                    if len(suggestions) >= limit:
                        return suggestions

        # Check regions
        for st in self._stories.values():
            if st.region_or_community and q in st.region_or_community.lower():
                key = ("region", st.region_or_community)
                if key not in seen:
                    suggestions.append(SearchSuggestion(
                        text=st.region_or_community,
                        suggestion_type="region",
                        country_code=st.country_code,
                    ))
                    seen.add(key)
                if len(suggestions) >= limit:
                    return suggestions

        return suggestions[:limit]

    # --- Source Registry Queries ---

    def list_sources(self) -> list[dict[str, Any]]:
        """List all external sources and API registries."""
        self._ensure_loaded()
        return self._sources

    def get_source(self, source_id: str) -> Optional[dict[str, Any]]:
        """Retrieve a specific source registry entry by ID."""
        self._ensure_loaded()
        return self._sources_by_id.get(source_id)

    def get_story_sources(self, story_id: str) -> Optional[list[StorySource]]:
        """Retrieve authentic bibliographic sources for a specific story."""
        story = self.get_story(story_id)
        if not story:
            return None
        return story.sources


# Singleton repository instance
story_repository = StoryRepository()
