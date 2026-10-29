"""Central Curated Folklore and Urban Legend Registry for KathaYantra.

Aggregates curated, verified, and policy-compliant story records across all 15 countries.
"""

from typing import Optional
from app.curation.countries.br_brazil import ALL_RECORDS as BR_RECORDS
from app.curation.countries.cn_china import ALL_RECORDS as CN_RECORDS
from app.curation.countries.de_germany import ALL_RECORDS as DE_RECORDS
from app.curation.countries.eg_egypt import ALL_RECORDS as EG_RECORDS
from app.curation.countries.gb_britain import ALL_RECORDS as GB_RECORDS
from app.curation.countries.gr_greece import ALL_RECORDS as GR_RECORDS
from app.curation.countries.id_indonesia import ALL_RECORDS as ID_RECORDS
from app.curation.countries.ie_ireland import ALL_RECORDS as IE_RECORDS
from app.curation.countries.in_india import ALL_RECORDS as IN_RECORDS
from app.curation.countries.jp_japan import ALL_RECORDS as JP_RECORDS
from app.curation.countries.kr_korea import ALL_RECORDS as KR_RECORDS
from app.curation.countries.mx_mexico import ALL_RECORDS as MX_RECORDS
from app.curation.countries.ng_nigeria import ALL_RECORDS as NG_RECORDS
from app.curation.countries.ph_philippines import ALL_RECORDS as PH_RECORDS
from app.curation.countries.us_usa import ALL_RECORDS as US_RECORDS
from app.schemas.story import StoryRecord

COUNTRY_REGISTRY: dict[str, list[StoryRecord]] = {
    "BR": BR_RECORDS,
    "CN": CN_RECORDS,
    "DE": DE_RECORDS,
    "EG": EG_RECORDS,
    "GB": GB_RECORDS,
    "GR": GR_RECORDS,
    "ID": ID_RECORDS,
    "IE": IE_RECORDS,
    "IN": IN_RECORDS,
    "JP": JP_RECORDS,
    "KR": KR_RECORDS,
    "MX": MX_RECORDS,
    "NG": NG_RECORDS,
    "PH": PH_RECORDS,
    "US": US_RECORDS,
}


def get_curated_records_for_country(country_code: str) -> list[StoryRecord]:
    """Retrieve all curated records (folklore and urban legends) for a country."""
    return COUNTRY_REGISTRY.get(country_code.upper(), [])


def get_all_curated_records() -> list[StoryRecord]:
    """Retrieve all 300 curated records across all 15 countries."""
    all_recs: list[StoryRecord] = []
    for code in sorted(COUNTRY_REGISTRY.keys()):
        all_recs.extend(COUNTRY_REGISTRY[code])
    return all_recs


ALL_CURATED_RECORDS: list[StoryRecord] = get_all_curated_records()


def get_curated_record_by_id(record_id: str) -> Optional[StoryRecord]:
    """Retrieve a single curated record by unique record ID."""
    prefix = record_id[:2].upper()
    for rec in COUNTRY_REGISTRY.get(prefix, []):
        if rec.id == record_id:
            return rec
    return None
