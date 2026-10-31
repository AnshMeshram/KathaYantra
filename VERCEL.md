# Deploying KathaYantra to Vercel 🚀

KathaYantra is completely pre-configured and optimized for **1-click, zero-config deployment on Vercel**.

---

## ⚡ Quick Deployment Steps (1-Click via Vercel Dashboard)

1. **Log in to Vercel** at [vercel.com](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Import your GitHub repository: `AnshMeshram/KathaYantra` (or your fork).
4. In the **Configure Project** screen:
   - **Framework Preset**: `Next.js` (detected automatically)
   - **Root Directory**: Click **Edit** and select **`frontend`** 👈 *(Crucial Step)*
   - **Build and Output Settings**: Leave as default (`pnpm build`, `.next`)
5. Click **"Deploy"**.

That's it! In ~60 seconds, your digital museum and interactive cartographic atlas will be live.

---

## 🔧 Environment Variables (Optional)

The application is **100% self-contained**: all 300 folklore & urban legend records, 15 country archives, full-text search, and in-memory ZIP export packs run natively inside Next.js API Route Handlers.

If you wish to customize runtime behavior, you can optionally configure these in **Vercel Project Settings → Environment Variables**:

| Variable | Default (if omitted) | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_BASE_URL` | *blank* (uses internal API) | Set to an external FastAPI backend URL if hosted separately (e.g. `https://api.kathayantra.com`). |
| `NEXT_PUBLIC_API_PREFIX` | `/api/v1` | Base prefix for REST API endpoints. |
| `NEXT_PUBLIC_APP_NAME` | `KathaYantra — The Haunted Atlas` | Brand application name. |

---

## 🏛️ What Works Out-of-the-Box on Vercel

- **Interactive 2D World Map:** Custom Japanese woodblock & washi cartography.
- **15 National Archives:** Verified folklore & urban legends (`IN`, `JP`, `MX`, `BR`, `US`, `CN`, `DE`, `EG`, `GB`, `GR`, `ID`, `IE`, `KR`, `NG`, `PH`).
- **Spider-Silk Regional Connectors:** Leaflet-to-card SVG topological connection lines.
- **Dedicated Discovery Routes:** `/explore`, `/folklore`, `/urban-legends`, and `/countries/[code]`.
- **Archival Pack ZIP Exports:** Generates standard ZIP archives with `README.md`, `stories.json`, `stories.csv`, citations, and licenses directly from serverless functions.
- **Zero-Dependency Fallback:** Fast in-memory responses with 0ms cold starts.

---

## 🛠️ Local Production Verification

To test the production build locally before pushing:

```bash
cd frontend
pnpm install
pnpm run build
pnpm start
```
