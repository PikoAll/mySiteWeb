// Export the brand kit PNGs from the SVGs in images/brand/ (not used by the
// site: they are for social profiles, print, the avatar project).
// Needs Playwright (not a site dependency):
//   npm i playwright && npx playwright install chromium
//   node scripts/export_brand_png.mjs [OUT_DIR]   (default images/brand)
import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const BRAND = join(dirname(fileURLToPath(import.meta.url)), "..", "images", "brand");
const OUT = process.argv[2] || BRAND;
const BG = "#0d0f12"; // --color-bg
mkdirSync(OUT, { recursive: true });

const svg = (name) => readFileSync(join(BRAND, name), "utf8");
// [file, svg, width, height, padding px, backgrounds]
const JOBS = [
  ["pikobit-symbol", "pikobit-symbol.svg", 1024, 1024, 72, ["transparent", BG]],
  ["pikobit-wordmark", "pikobit-wordmark.svg", 2000, 394, 0, ["transparent", BG]],
  ["header-circuit", "header-circuit.svg", 2400, 300, 0, [BG]],
];

const browser = await chromium.launch();
const page = await browser.newPage();
for (const [name, file, w, h, pad, bgs] of JOBS) {
  await page.setViewportSize({ width: w, height: h });
  for (const bg of bgs) {
    await page.setContent(
      `<body style="margin:0;background:${bg}"><div style="box-sizing:border-box;width:${w}px;height:${h}px;padding:${pad}px;display:flex">` +
        svg(file).replace("<svg ", '<svg width="100%" height="100%" ') +
        "</div></body>",
    );
    const suffix = bg === "transparent" ? "transparent" : "dark";
    await page.screenshot({ path: join(OUT, `${name}-${w}-${suffix}.png`), omitBackground: bg === "transparent" });
  }
}
await browser.close();
console.log("brand PNGs written to", OUT);
