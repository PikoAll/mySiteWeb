// From the home to every city page: the list links and the map dots.
import { test, expect } from "@playwright/test";
import { CITIES } from "./pages.mjs";

test.use({ viewport: { width: 1440, height: 900 } });

// The scenes do not start on weak devices (hardwareConcurrency <= 2): force
// a normal one, so the map tests run the same on any machine or CI.
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() =>
    Object.defineProperty(Navigator.prototype, "hardwareConcurrency", { get: () => 8 }),
  );
});

// Wait for a still map: fonts loaded, links placed, same box twice in a row.
const settledBox = async (page, locator) => {
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator(".fx-map-links[data-ready]")).toBeVisible({ timeout: 15_000 });
  let prev = null;
  for (let i = 0; i < 20; i++) {
    const box = await locator.boundingBox();
    if (prev && box && Math.abs(box.x - prev.x) < 0.5 && Math.abs(box.y - prev.y) < 0.5) return box;
    prev = box;
    await page.waitForTimeout(150);
  }
  throw new Error("map links never settled");
};

test("home -> zones link -> dove lavoro", async ({ page }) => {
  await page.goto("index.html");
  await page.getByRole("link", { name: "ecco come lavoro e in quali zone" }).click();
  await expect(page).toHaveURL(/dove-lavoro\.html$/);
});

test("home hero: 'Monopoli' links the Monopoli page", async ({ page }) => {
  await page.goto("index.html");
  await page.locator(".intro-container p a", { hasText: /^Monopoli$/ }).click();
  await expect(page).toHaveURL(/programmatore-monopoli\.html$/);
});

for (const city of CITIES) {
  test(`dove-lavoro list -> ${city}`, async ({ page }) => {
    await page.goto("dove-lavoro.html");
    const chip = page.locator(`main .city-grid li.card--link:has(a[href="programmatore-${city}.html"])`);
    await expect(chip).toHaveCount(1);
    await expect(chip).toHaveCSS("cursor", "pointer");
    // click the chip edge, not the text: the whole chip is the link
    await chip.scrollIntoViewIfNeeded();
    await page.waitForTimeout(700); // the section reveal animation
    const box = await chip.boundingBox();
    await page.mouse.click(box.x + 6, box.y + box.height / 2);
    await expect(page).toHaveURL(new RegExp(`programmatore-${city}\\.html$`));
  });

  for (const width of [1280, 1440, 1920]) test(`dove-lavoro map ${width}px -> ${city}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("dove-lavoro.html");
    const dot = page.locator(`.fx-map-links a[data-city="${city}"]`);
    // a real mouse click at the dot: proves nothing covers it
    const box = await settledBox(page, dot);
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await expect(page).toHaveURL(new RegExp(`programmatore-${city}\\.html$`));
  });
}

test("the map dots sit on the drawn cities", async ({ page }) => {
  await page.goto("dove-lavoro.html");
  await expect(page.locator(".fx-map-links a")).toHaveCount(12, { timeout: 15_000 });
  await settledBox(page, page.locator(".fx-map-links a").first());
  await page.waitForTimeout(300); // one more painted frame
  // the canvas paints a bright dot at every city: sample it under each link
  const misses = await page.evaluate(() => {
    const canvas = document.querySelector(".fx-canvas");
    const cr = canvas.getBoundingClientRect();
    const g = canvas.getContext("2d");
    const sx = canvas.width / cr.width;
    return [...document.querySelectorAll(".fx-map-links a")].filter((a) => {
      const r = a.getBoundingClientRect();
      const x = (r.left + r.width / 2 - cr.left) * sx;
      const y = (r.top + r.height / 2 - cr.top) * sx;
      const d = g.getImageData(x - 6 * sx, y - 6 * sx, 12 * sx, 12 * sx).data;
      let max = 0;
      for (let i = 3; i < d.length; i += 4) max = Math.max(max, d[i]);
      return max < 120;
    }).map((a) => a.dataset.city);
  });
  expect(misses).toEqual([]);
});

test("narrow screens: no map links over the text", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("dove-lavoro.html");
  await page.waitForTimeout(4000);
  await expect(page.locator(".fx-map-links a:visible")).toHaveCount(0);
});

test("city page: parent menu entry, breadcrumb, zone chips", async ({ page }) => {
  await page.goto("programmatore-monopoli.html");
  const dove = page.locator("#navbar a", { hasText: "Dove lavoro" });
  await expect(dove).toHaveClass(/nav-parent/);
  await expect(dove).not.toHaveAttribute("aria-current", /.*/);
  await expect(page.locator("#navbar [aria-current]")).toHaveCount(0);
  const crumb = page.locator("nav.breadcrumb");
  await expect(crumb).toBeVisible();
  await expect(crumb).toHaveText(/Home\s*›\s*Dove lavoro\s*›\s*Monopoli/);
  await crumb.getByRole("link", { name: "Dove lavoro" }).click();
  await expect(page).toHaveURL(/dove-lavoro\.html$/);
  await expect(page.locator("#navbar a", { hasText: "Dove lavoro" })).toHaveAttribute("aria-current", "page");
});
