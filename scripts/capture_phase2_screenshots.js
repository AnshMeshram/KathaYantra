/**
 * KathaYantra Phase 2 Section 1 Real Screenshot Capture Script.
 * Captures desktop above-fold, full-page editorial, and mobile responsive views.
 */

const path = require("path");
const puppeteer = require(path.join(__dirname, "../frontend/node_modules/puppeteer-core"));

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
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
    // 1. Desktop Above-Fold View (1440x960)
    console.log("Capturing phase-2-section-1-desktop.png...");
    await page.setViewport({ width: 1440, height: 960 });
    await page.goto(BASE_URL, { waitUntil: "networkidle0", timeout: 35000 });
    await new Promise((r) => setTimeout(r, 2500)); // allow fonts and layout to settle
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-1-desktop.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-1-desktop.png");

    // 2. Full-Page Editorial Scroll View (1440px wide)
    console.log("Capturing phase-2-section-1-fullpage.png...");
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-1-fullpage.png"),
      fullPage: true,
    });
    console.log("Saved phase-2-section-1-fullpage.png");

    // 3. Mobile View (390x844)
    console.log("Capturing phase-2-section-1-mobile.png...");
    await page.setViewport({ width: 390, height: 844, isMobile: true });
    await page.goto(BASE_URL, { waitUntil: "networkidle0", timeout: 35000 });
    await new Promise((r) => setTimeout(r, 2000));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-1-mobile.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-1-mobile.png");

    console.log("All 3 Phase 2 Section 1 screenshots captured successfully!");
  } catch (err) {
    console.error("Screenshot error:", err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
