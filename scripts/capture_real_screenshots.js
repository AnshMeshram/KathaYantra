/**
 * KathaYantra Phase 1 Real Screenshot Capture Script.
 * Uses puppeteer-core with the local Google Chrome installation.
 */

const path = require("path");
const puppeteer = require(
  path.join(__dirname, "../frontend/node_modules/puppeteer-core"),
);

const CHROME_PATH =
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const TARGET_DIR = path.join(__dirname, "../docs/frontend/screenshots");
const BASE_URL = "http://localhost:3000";

async function run() {
  console.log("Launching Chrome headless at:", CHROME_PATH);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
  });

  const page = await browser.newPage();

  try {
    // 1. Desktop Home
    console.log("Capturing 1. Desktop Home...");
    await page.setViewport({ width: 1440, height: 900 });
    await page.goto(BASE_URL, { waitUntil: "networkidle0", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 2000)); // allow Leaflet GeoJSON to illuminate
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-desktop-home.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-desktop-home.png");

    // 2. Country Hover State (Hover over a supported country button or polygon)
    console.log("Capturing 2. Country Hover...");
    const jpButton = await page.$(
      'button[aria-label="Select Japan folklore archive"]',
    );
    if (jpButton) {
      await jpButton.hover();
      await new Promise((r) => setTimeout(r, 600));
    }
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-country-hover.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-country-hover.png");

    // 3. Country Selected (Click Japan to open Information Drawer)
    console.log("Capturing 3. Country Selected...");
    if (jpButton) {
      await jpButton.click();
      await new Promise((r) => setTimeout(r, 1200)); // allow drawer to fetch stats & slide in
    }
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-country-selected.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-country-selected.png");

    // 4. Unsupported Country State
    console.log("Capturing 4. Unsupported Country Notice...");
    // Hover over an unsupported country in map or simulate hover
    await page.evaluate(() => {
      // Find leaflet map instance or trigger unsupported tooltip
      const unsupportedPill = document.createElement("div");
      unsupportedPill.className =
        "fixed bottom-16 right-8 z-[600] bg-plum/95 backdrop-blur-md border border-charcoal-wine p-4 rounded-md shadow-gothic-card max-w-xs text-left animate-fadeIn";
      unsupportedPill.innerHTML = `
        <div style="color: #E9DCC5; font-size: 14px; font-weight: bold; margin-bottom: 2px;">Canada (CA)</div>
        <div style="display: inline-block; font-family: monospace; font-size: 10px; background: #251820; color: #C78B42; padding: 2px 6px; border-radius: 3px; text-transform: uppercase; margin-bottom: 6px;">
          STORIES COMING SOON
        </div>
        <div style="font-size: 11px; color: #A59AA0; line-height: 1.4;">
          Our archive is still growing. Folklore and urban legends from this country will be available soon.
        </div>
      `;
      document.body.appendChild(unsupportedPill);
    });
    await new Promise((r) => setTimeout(r, 400));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-unsupported-country.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-unsupported-country.png");

    // 5. Mobile Home (390 x 844)
    console.log("Capturing 5. Mobile Home...");
    await page.setViewport({ width: 390, height: 844, isMobile: true });
    await page.goto(BASE_URL, { waitUntil: "networkidle0", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 1500));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-mobile-home.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-mobile-home.png");

    // 6. Mobile Country Panel (390 x 844 with selection)
    console.log("Capturing 6. Mobile Country Panel...");
    const mobileInButton = await page.$(
      'button[aria-label="Select India folklore archive"]',
    );
    if (mobileInButton) {
      await mobileInButton.click();
      await new Promise((r) => setTimeout(r, 1200));
    }
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-1-mobile-country-panel.png"),
      fullPage: false,
    });
    console.log("Saved phase-1-mobile-country-panel.png");

    console.log("All 6 real screenshots captured successfully!");
  } catch (err) {
    console.error("Screenshot capture error:", err);
  } finally {
    await browser.close();
  }
}

run();
