"""Candidate Normalization Service for KathaYantra Ingestion Pipelines."""

import html
import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from app.schemas.country import SUPPORTED_COUNTRY_CODES
from app.schemas.import_candidate import ImportCandidate
from app.schemas.story import CategoryEnum


class CandidateNormalizer:
    """Provides uniform string cleaning, URL normalization, and country/category sanitization."""

    TRACKING_PARAM_PREFIXES = ("utm_", "fbclid", "gclid", "ref", "source")

    @classmethod
    def clean_title(cls, raw_title: str) -> str:
        """Unescape HTML entities, normalize whitespace, and trim title."""
        if not raw_title:
            return "Untitled"
        text = html.unescape(raw_title)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @classmethod
    def clean_url(cls, raw_url: Optional[str]) -> Optional[str]:
        """Strip tracking parameters, fragments, and ensure valid scheme."""
        if not raw_url:
            return None
        url = raw_url.strip()
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return url

        # Strip utm and tracking query params
        if parsed.query:
            filtered_params = [
                (k, v)
                for k, v in parse_qsl(parsed.query)
                if not any(k.lower().startswith(prefix) for prefix in cls.TRACKING_PARAM_PREFIXES)
            ]
            new_query = urlencode(filtered_params)
        else:
            new_query = ""

        cleaned = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            new_query,
            "",  # strip fragment
        ))
        return cleaned

    @classmethod
    def normalize_country_code(cls, country_code: Optional[str]) -> Optional[str]:
        """Validate and return normalized uppercase country code if in 15 supported countries."""
        if not country_code:
            return None
        upper = country_code.strip().upper()
        if upper in SUPPORTED_COUNTRY_CODES:
            return upper
        return None

    @classmethod
    def normalize_category(cls, category: Optional[str]) -> Optional[CategoryEnum]:
        """Coerce string category into CategoryEnum."""
        if not category:
            return None
        cat_clean = category.strip().lower()
        if cat_clean in ("folklore", "folk", "traditional"):
            return CategoryEnum.FOLKLORE
        if cat_clean in ("urban_legend", "urban_legends", "modern_legend", "urban"):
            return CategoryEnum.URBAN_LEGEND
        return None

    @classmethod
    def normalize_candidate(cls, candidate: ImportCandidate) -> ImportCandidate:
        """Apply normalization in-place to an ImportCandidate."""
        candidate.raw_title = cls.clean_title(candidate.raw_title)
        if candidate.raw_url:
            candidate.raw_url = cls.clean_url(candidate.raw_url)
        if candidate.proposed_country_code:
            candidate.proposed_country_code = cls.normalize_country_code(candidate.proposed_country_code)
        return candidate
