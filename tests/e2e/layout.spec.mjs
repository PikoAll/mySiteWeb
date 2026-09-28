// Card grids never leave one orphan card on the last row, the hero text
// never leaves its box, no page scrolls sideways. Every page, every width.
import { test, expect } from "@playwright/test";
import { PAGES } from "./pages.mjs";

const WIDTHS = [360, 390, 768, 1024, 1280, 1440, 1920, 2560];
const GRIDS = ".card-grid, .carousel-track, .steps, .articles-section, .city-grid";

for (const width of WIDTHS) {
  test.describe(`${width}px`, () => {
    test.use({ viewport: { width, height: 900 } });

    for (const page of PAGES) {
      test(page, async ({ page: p }) => {
        await p.goto(page);
        const report = await p.evaluate((sel) => {
          const out = { orphans: [], narrow: [], hero: [], overflow: 0 };
          for (const g of document.querySelectorAll(sel)) {
            const items = [...g.children].filter((c) => c.getClientRects().length);
            if (items.length < 2) continue;
            // a scrolling carousel shows one row by design
            if (g.scrollWidth > g.clientWidth + 2) continue;
            for (const c of items)
              if (c.getBoundingClientRect().width < 150)
                out.narrow.push(`${g.className} ${Math.round(c.getBoundingClientRect().width)}px`);
            const rows = new Map();
            for (const c of items) {
              const top = Math.round(c.getBoundingClientRect().top);
              rows.set(top, (rows.get(top) || 0) + 1);
            }
            const counts = [...rows.values()];
            if (counts.length > 1 && counts.at(-1) === 1 && Math.max(...counts) > 1)
              out.orphans.push(`${g.className} rows=${counts.join("+")}`);
          }
          for (const el of document.querySelectorAll(".intro-container p")) {
            const r = el.getBoundingClientRect();
            const box = el.closest(".intro-container").getBoundingClientRect();
            if (r.left < box.left - 1 || r.right > box.right + 1 || r.left < 0 || r.right > innerWidth)
              out.hero.push(el.textContent.trim().slice(0, 40));
            // centred: same room left and right inside the box
            if (Math.abs(r.left - box.left - (box.right - r.right)) > 2)
              out.hero.push("off-centre: " + el.textContent.trim().slice(0, 40));
            if (el.scrollWidth > el.clientWidth + 1) out.hero.push("overflow: " + el.textContent.trim().slice(0, 40));
          }
          out.overflow = document.documentElement.scrollWidth - innerWidth;
          return out;
        }, GRIDS);
        expect(report.orphans, "orphan card on the last row").toEqual([]);
        expect(report.narrow, "card narrower than 150px").toEqual([]);
        expect(report.hero, "hero text outside its box").toEqual([]);
        expect(report.overflow, "horizontal page scroll").toBeLessThanOrEqual(0);
      });
    }
  });
}

test.describe("home, wide screens", () => {
  for (const width of [1280, 1440, 1920, 2560]) {
    test(`the 5 services and the 5 reasons sit on one row at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("index.html");
      for (const id of ["#servizi", "#perche-pikobit"]) {
        const tops = await page.$$eval(`${id} .carousel-track > li`, (els) =>
          els.map((e) => Math.round(e.getBoundingClientRect().top)),
        );
        expect(tops).toHaveLength(5);
        expect(new Set(tops).size, id).toBe(1);
      }
    });
  }
});
