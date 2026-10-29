"""Candidate Deduplication and Cultural Variant Analysis Service."""

import hashlib
import re
from typing import Optional
from app.schemas.import_candidate import CandidateDispositionEnum, ImportCandidate


class CandidateDeduplicator:
    """Detects exact duplicates and flags title/motif similarities without erasing cultural variants."""

    @staticmethod
    def compute_fingerprint(candidate: ImportCandidate) -> str:
        """Compute deterministic SHA-256 fingerprint from source, URL, and normalized title."""
        source_id = candidate.source_registry_id or "unknown"
        ext_id = candidate.external_id or ""
        url = (candidate.raw_url or "").strip().lower()
        title = candidate.raw_title.strip().lower()

        raw_str = f"{source_id}:{ext_id}:{url}:{title}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_title_tokens(title: str) -> set[str]:
        """Extract alphanumeric token set from title for Jaccard similarity comparison."""
        words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", title.lower())
        stopwords = {"the", "and", "for", "with", "story", "tale", "legend", "myth", "about"}
        return {w for w in words if w not in stopwords}

    @classmethod
    def calculate_title_similarity(cls, title_a: str, title_b: str) -> float:
        """Calculate Jaccard similarity coefficient between two titles."""
        tokens_a = cls.compute_title_tokens(title_a)
        tokens_b = cls.compute_title_tokens(title_b)
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return intersection / union if union > 0 else 0.0

    @classmethod
    def process_candidate(
        cls,
        candidate: ImportCandidate,
        seen_fingerprints: set[str],
        known_candidates: Optional[list[ImportCandidate]] = None,
    ) -> ImportCandidate:
        """Evaluate candidate for duplicate status or potential cultural variant review."""
        fp = cls.compute_fingerprint(candidate)

        if fp in seen_fingerprints:
            candidate.disposition = CandidateDispositionEnum.DUPLICATE_CANDIDATE
            candidate.review_notes = (
                f"{candidate.review_notes or ''} [Deduplication: Exact duplicate detected (fingerprint {fp[:8]}).]"
            ).strip()
            return candidate

        seen_fingerprints.add(fp)

        # Check for title similarities in known candidates from DIFFERENT cultures
        if known_candidates:
            for existing in known_candidates:
                if existing.candidate_id == candidate.candidate_id:
                    continue
                sim = cls.calculate_title_similarity(candidate.raw_title, existing.raw_title)
                if sim >= 0.45:
                    # High similarity - flag as possible variant rather than merging!
                    existing_country = existing.proposed_country_code or "Unknown"
                    cand_country = candidate.proposed_country_code or "Unknown"
                    note = (
                        f" [Variant Notice: Title has {sim:.0%} lexical similarity with "
                        f"{existing.candidate_id} ('{existing.raw_title}', {existing_country}). "
                        f"Keep separate to preserve regional traditions.]"
                    )
                    candidate.review_notes = f"{candidate.review_notes or ''}{note}".strip()
                    break

        return candidate
