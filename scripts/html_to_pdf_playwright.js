const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright-core");

async function main() {
  const input = process.argv[2];
  const output = process.argv[3];
  if (!input || !output) {
    throw new Error("Usage: node html_to_pdf_playwright.js <input.html> <output.pdf>");
  }

  const browser = await chromium.launch({
    headless: true,
    executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    args: ["--disable-gpu", "--no-sandbox"],
  });

  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1800 } });
    await page.goto(pathToFileURL(path.resolve(input)).href, { waitUntil: "networkidle" });
    await page.emulateMedia({ media: "screen" });
    await page.pdf({
      path: output,
      format: "A4",
      landscape: true,
      printBackground: true,
      preferCSSPageSize: false,
      margin: {
        top: "10mm",
        right: "8mm",
        bottom: "10mm",
        left: "8mm",
      },
    });
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
