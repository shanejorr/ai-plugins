#!/usr/bin/env node
// Render a LinkedIn profile in headless Chromium and print the page text.
// Usage: node scrape_profile.mjs <username>
// Exit codes: 0 = text printed, 1 = usage/launch error, 2 = navigation failed.
// The caller is responsible for checking the output for LinkedIn's authwall.

import { createRequire } from "node:module";

const username = process.argv[2];
if (!username) {
  console.error("Usage: node scrape_profile.mjs <linkedin-username>");
  process.exit(1);
}

let chromium;
try {
  const require = createRequire(import.meta.url);
  ({ chromium } = require("playwright"));
} catch {
  console.error(
    "Playwright is not installed. Run: npm install playwright && npx playwright install chromium"
  );
  process.exit(1);
}

const url = `https://www.linkedin.com/in/${encodeURIComponent(username)}/`;

const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({
    // A realistic desktop UA lowers the odds of an instant bot block.
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    viewport: { width: 1280, height: 900 },
    locale: "en-US",
  });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  // Give client-side rendering a moment, then scroll to trigger lazy sections.
  await page.waitForTimeout(3000);
  for (let i = 0; i < 5; i++) {
    await page.mouse.wheel(0, 1200);
    await page.waitForTimeout(500);
  }
  const text = await page.evaluate(() => document.body.innerText);
  console.log(text);
} catch (err) {
  console.error(`Navigation failed: ${err.message}`);
  process.exit(2);
} finally {
  await browser.close();
}
