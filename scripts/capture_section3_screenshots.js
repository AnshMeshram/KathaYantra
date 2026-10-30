/**
 * Puppeteer Headless Chrome Screenshot Capture for Phase 2 / Section 3
 */

const path = require("path");
const fs = require("fs");
const puppeteer = require(path.resolve(__dirname, "../frontend/node_modules/puppeteer-core"));

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const BASE_URL = "http://localhost:3000";
const TARGET_DIR = path.resolve(__dirname, "../docs/frontend/screenshots");

async function run() {
  if (!fs.existsSync(TARGET_DIR)) {
    fs.mkdirSync(TARGET_DIR, { recursive: true });
  }

  console.log(`Launching Chrome headless at: ${CHROME_PATH}`);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });

    // 1. Explore Page
    console.log("1. Capturing phase-2-section-3-explore.png...");
    await page.goto(`${BASE_URL}/explore`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("article", { timeout: 25000 }).catch(() => {});
    await new Promise((r) => setTimeout(r, 3500));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-3-explore.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-3-explore.png");

    // 2. Folklore Collection Page
    console.log("2. Capturing phase-2-section-3-folklore.png...");
    await page.goto(`${BASE_URL}/folklore`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("article", { timeout: 25000 }).catch(() => {});
    await new Promise((r) => setTimeout(r, 3500));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-3-folklore.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-3-folklore.png");

    // 3. Urban Legends Collection Page
    console.log("3. Capturing phase-2-section-3-urban-legends.png...");
    await page.goto(`${BASE_URL}/urban-legends`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("article", { timeout: 25000 }).catch(() => {});
    await new Promise((r) => setTimeout(r, 3500));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-3-urban-legends.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-3-urban-legends.png");

    // 4. Country Collections Page (/countries/IN)
    console.log("4. Capturing phase-2-section-3-country-collections.png...");
    await page.goto(`${BASE_URL}/countries/IN`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForSelector("article", { timeout: 25000 }).catch(() => {});
    await new Promise((r) => setTimeout(r, 4000));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-3-country-collections.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-3-country-collections.png");

    // 5. Mobile Responsive View (390x844 on /explore)
    console.log("5. Capturing phase-2-section-3-mobile.png...");
    await page.setViewport({ width: 390, height: 844, isMobile: true });
    await page.goto(`${BASE_URL}/explore`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await new Promise((r) => setTimeout(r, 3000));
    await page.screenshot({
      path: path.join(TARGET_DIR, "phase-2-section-3-mobile.png"),
      fullPage: false,
    });
    console.log("Saved phase-2-section-3-mobile.png");

    console.log("All 5 Section 3 screenshots captured successfully!");
  } catch (err) {
    console.error("Screenshot error:", err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
