"""Download and normalize Natural Earth 1:110m GeoJSON for KathaYantra."""

from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
GEO_DIR = ROOT_DIR / "frontend" / "public" / "data" / "geo"
GEO_DIR.mkdir(parents=True, exist_ok=True)

OUT_GEOJSON = GEO_DIR / "countries.geojson"
OUT_SOURCE = GEO_DIR / "geojson-source.json"

URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
FALLBACK_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

def fetch_and_normalize():
    print(f"Fetching GeoJSON from {URL}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KathaYantra/1.0"}
    req = urllib.request.Request(URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Primary URL failed: {e}. Trying fallback: {FALLBACK_URL}")
        req2 = urllib.request.Request(FALLBACK_URL, headers=headers)
        with urllib.request.urlopen(req2, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
    features = data.get("features", [])
    print(f"Loaded {len(features)} country features. Normalizing properties...")
    
    # Supported countries mapping
    # Note Natural Earth quirks: ISO_A2 can be -99 or missing in some datasets, check ISO_A2_EH or ADM0_A3 or NAME
    normalized_features = []
    supported_found = set()
    
    SUPPORTED = {"IN", "US", "JP", "MX", "IE", "GB", "BR", "GR", "CN", "NG", "KR", "PH", "ID", "EG", "DE"}
    
    NAME_TO_CODE = {
        "United States of America": "US",
        "United States": "US",
        "United Kingdom": "GB",
        "France": "FR",
        "Norway": "NO",
        "S. Korea": "KR",
        "Republic of Korea": "KR",
        "South Korea": "KR",
    }
    
    for f in features:
        props = f.get("properties", {})
        code = (
            props.get("ISO_A2") 
            or props.get("ISO_A2_EH") 
            or props.get("iso_a2") 
            or props.get("wb_a2") 
            or props.get("ISO3166-1-Alpha-2")
            or ""
        ).upper()
        
        name = props.get("NAME") or props.get("name") or props.get("ADMIN") or ""
        
        if code in ("-99", "") and name in NAME_TO_CODE:
            code = NAME_TO_CODE[name]
            
        # Specific check for Natural Earth UK / GB
        if name in ("United Kingdom", "UK") or code in ("UK", "-99") and "Kingdom" in name:
            code = "GB"
            
        # Ensure properties have canonical iso_a2 and name
        props["iso_a2"] = code
        props["ISO_A2"] = code
        props["name"] = name
        props["is_supported"] = code in SUPPORTED
        
        if code in SUPPORTED:
            supported_found.add(code)
            
        f["properties"] = props
        normalized_features.append(f)
        
    data["features"] = normalized_features
    
    with open(OUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        
    print(f"Saved {OUT_GEOJSON} ({len(normalized_features)} features). Supported found: {sorted(supported_found)}")
    
    # Write geojson-source.json
    source_meta = {
        "dataset_name": "Natural Earth 1:110m Admin 0 Countries",
        "original_source_url": URL,
        "fallback_url": FALLBACK_URL,
        "version": "5.1.1",
        "license": "Public Domain",
        "license_url": "https://www.naturalearthdata.com/about/terms-of-use/",
        "attribution": "Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "total_features": len(normalized_features),
        "supported_countries_detected": sorted(supported_found),
        "supported_countries_expected": sorted(SUPPORTED),
        "all_supported_present": SUPPORTED == supported_found
    }
    
    with open(OUT_SOURCE, "w", encoding="utf-8") as f:
        json.dump(source_meta, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {OUT_SOURCE} successfully.")

if __name__ == "__main__":
    fetch_and_normalize()

