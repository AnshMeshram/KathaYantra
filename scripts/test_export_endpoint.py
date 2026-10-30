"""Direct test of the export endpoint against the running server."""

import io
import json
import urllib.request
import zipfile

BASE = "http://127.0.0.1:8000/api/v1/export/pack"

# 1. Test Folklore Export
req = urllib.request.urlopen(f"{BASE}?category=folklore")
assert req.status == 200, f"Expected 200 got {req.status}"
assert "kathayantra-folklore-archive.zip" in req.headers.get("Content-Disposition")
zf = zipfile.ZipFile(io.BytesIO(req.read()))
assert "KathaYantra-Archive/stories.json" in zf.namelist()
stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
assert len(stories) == 150, f"Expected 150 stories, got {len(stories)}"
print(f"[PASS] Folklore pack passed: {len(stories)} stories")

# 2. Test Urban Legend Export
req = urllib.request.urlopen(f"{BASE}?category=urban_legend")
assert req.status == 200
zf = zipfile.ZipFile(io.BytesIO(req.read()))
stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
assert len(stories) == 150, f"Expected 150 stories, got {len(stories)}"
print(f"[PASS] Urban legends pack passed: {len(stories)} stories")

# 3. Test Country Specific Export (IN)
req = urllib.request.urlopen(f"{BASE}?category=folklore&country_code=IN")
assert req.status == 200
zf = zipfile.ZipFile(io.BytesIO(req.read()))
stories = json.loads(zf.read("KathaYantra-Archive/stories.json").decode("utf-8"))
assert len(stories) == 10, f"Expected 10 stories, got {len(stories)}"
print(f"[PASS] Country pack (IN folklore) passed: {len(stories)} stories")

# 4. Test Unsupported Country (404)
try:
    urllib.request.urlopen(f"{BASE}?country_code=ZZ")
    assert False, "Should have raised 404"
except urllib.error.HTTPError as e:
    assert e.code == 404
    data = json.loads(e.read().decode("utf-8"))
    assert data["error_code"] == "COUNTRY_NOT_SUPPORTED"
    print("[PASS] Unsupported country 404 passed")

# 5. Test Invalid Category (422)
try:
    urllib.request.urlopen(f"{BASE}?category=invalid")
    assert False, "Should have raised 422"
except urllib.error.HTTPError as e:
    assert e.code == 422
    print("[PASS] Invalid category 422 passed")

print("ALL 5 EXPORT TESTS PASSED SUCCESSFULLY!")
