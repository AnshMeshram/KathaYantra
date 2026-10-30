/**
 * Automated Verification Script: Test Leaflet Map Interactions & Ensure Zero Runtime Errors
 */

const path = require("path");
const puppeteer = require(path.resolve(__dirname, "../frontend/node_modules/puppeteer-core"));

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const BASE_URL = "http://localhost:3000";

async function verify() {
  console.log("Launching Chrome headless to test map interactions...");
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  const capturedErrors = [];
  page.on("pageerror", (err) => {
    console.error("PAGE ERROR DETECTED:", err.message);
    capturedErrors.push(err.message);
  });
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.error("CONSOLE ERROR:", msg.text());
    }
  });

  try {
    // 1. Test Homepage World Map
    console.log("\n[Test 1] Navigating to Homepage World Map...");
    await page.goto(`${BASE_URL}`, { waitUntil: "networkidle2", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 2000));

    console.log("Triggering Zoom In...");
    const zoomInBtn = await page.$("button[aria-label='Zoom in']");
    if (zoomInBtn) await zoomInBtn.click();
    await new Promise((r) => setTimeout(r, 800));

    console.log("Triggering Zoom Out...");
    const zoomOutBtn = await page.$("button[aria-label='Zoom out']");
    if (zoomOutBtn) await zoomOutBtn.click();
    await new Promise((r) => setTimeout(r, 800));

    // 2. Test Country Map Explorer (/countries/IN)
    console.log("\n[Test 2] Navigating to /countries/IN...");
    await page.goto(`${BASE_URL}/countries/IN`, { waitUntil: "networkidle2", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 3000));

    console.log("Triggering Country Map Zoom In & Zoom Out...");
    const cZoomIn = await page.$("button[aria-label='Zoom in']");
    if (cZoomIn) {
      await cZoomIn.click();
      await new Promise((r) => setTimeout(r, 600));
      await cZoomIn.click();
      await new Promise((r) => setTimeout(r, 600));
    }
    const cZoomOut = await page.$("button[aria-label='Zoom out']");
    if (cZoomOut) {
      await cZoomOut.click();
      await new Promise((r) => setTimeout(r, 600));
    }

    console.log("Triggering Category Filter Switch...");
    const buttons = await page.$$("button");
    for (const btn of buttons) {
      const text = await page.evaluate((el) => el.textContent, btn);
      if (text && text.includes("Folklore")) {
        await btn.click();
        console.log("Clicked Folklore filter");
        await new Promise((r) => setTimeout(r, 800));
        break;
      }
    }

    // Scroll wheel over map container
    console.log("Triggering mouse wheel over map...");
    const mapEl = await page.$(".leaflet-container");
    if (mapEl) {
      const box = await mapEl.boundingBox();
      if (box) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.mouse.wheel({ deltaY: -200 });
        await new Promise((r) => setTimeout(r, 800));
        await page.mouse.wheel({ deltaY: 200 });
        await new Promise((r) => setTimeout(r, 800));
      }
    }

    // 3. Navigate between pages to test unmount cleanup
    console.log("\n[Test 3] Navigating to /explore to test unmount safety...");
    await page.goto(`${BASE_URL}/explore`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 2000));

    console.log("\n[Test 4] Navigating back to /countries/JP...");
    await page.goto(`${BASE_URL}/countries/JP`, { waitUntil: "networkidle2", timeout: 30000 });
    await new Promise((r) => setTimeout(r, 2500));

    if (capturedErrors.length === 0) {
      console.log("\n[SUCCESS] All map interaction tests passed with 0 runtime errors!");
    } else {
      console.error(`\n[FAIL] Found ${capturedErrors.length} runtime error(s):`, capturedErrors);
      process.exit(1);
    }
  } catch (err) {
    console.error("Test failed with exception:", err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

verify();
