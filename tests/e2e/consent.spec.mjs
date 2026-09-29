// Cookie banner (scripts/consent.js): nothing reaches Google before "Accetta".
import { test, expect } from "@playwright/test";
import { PAGES } from "./pages.mjs";
import { decided, KEY } from "./consent-state.mjs";

const GOOGLE = /googletagmanager\.com|google-analytics\.com/;

// Empty browser: no saved choice.
test.use({ storageState: { cookies: [], origins: [] } });

// Record every request to Google; answer gtag.js with an empty script so the
// tests never call the real service.
const watchGoogle = async (page) => {
  const hits = [];
  await page.route(GOOGLE, (route) => {
    hits.push(route.request().url());
    route.fulfill({ status: 200, contentType: "text/javascript", body: "" });
  });
  return hits;
};

const banner = (page) => page.getByRole("dialog", { name: "Cookie su questo sito" });
const gaCookies = async (page) =>
  (await page.context().cookies()).filter((c) => c.name.startsWith("_ga"));
const saved = (page) => page.evaluate((k) => JSON.parse(localStorage.getItem(k)), KEY);
const consentCalls = (page) =>
  page.evaluate(() =>
    window.dataLayer.filter((a) => a[0] === "consent").map((a) => [a[1], a[2]]),
  );

test("before the choice: banner shown, no request to Google, no _ga cookie", async ({ page }) => {
  const hits = await watchGoogle(page);
  await page.goto("index.html");
  await expect(banner(page)).toBeVisible();
  await expect(banner(page).getByRole("link", { name: "Informativa cookie" })).toHaveAttribute(
    "href",
    /\/privacy\.html#cookie$/,
  );
  // scrolling or clicking elsewhere is not a consent
  await page.mouse.wheel(0, 2000);
  await page.locator("h1").first().click();
  await page.waitForTimeout(500);
  await expect(banner(page)).toBeVisible();
  expect(hits).toEqual([]);
  expect(await gaCookies(page)).toEqual([]);
  const calls = await consentCalls(page);
  expect(calls).toEqual([
    ["default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
    }],
  ]);
});

test("Accetta: gtag.js loads, only analytics_storage is granted", async ({ page }) => {
  const hits = await watchGoogle(page);
  await page.goto("websites.html");
  await banner(page).getByRole("button", { name: "Accetta", exact: true }).click();
  await expect(banner(page)).toHaveCount(0);
  await expect.poll(() => hits.length).toBe(1);
  expect(hits[0]).toContain("googletagmanager.com/gtag/js?id=G-TVGN1XBX7H");
  expect((await consentCalls(page)).at(-1)).toEqual(["update", { analytics_storage: "granted" }]);
  const config = await page.evaluate(() => window.dataLayer.find((a) => a[0] === "config"));
  expect(config[2]).toEqual({ allow_google_signals: false, allow_ad_personalization_signals: false });
  expect((await saved(page)).choice).toBe("granted");
  // next page: loads GA straight away, no banner
  await page.goto("about.html");
  await expect(banner(page)).toHaveCount(0);
  await expect.poll(() => hits.length).toBe(2);
});

test("Rifiuta: no GA, and the banner does not come back on reload", async ({ page }) => {
  const hits = await watchGoogle(page);
  await page.goto("index.html");
  await banner(page).getByRole("button", { name: "Rifiuta", exact: true }).click();
  await expect(banner(page)).toHaveCount(0);
  await page.reload();
  await page.goto("blog/" + PAGES.at(-1).split("/").at(-1));
  await page.waitForTimeout(300);
  await expect(banner(page)).toHaveCount(0);
  expect(hits).toEqual([]);
  expect((await saved(page)).choice).toBe("denied");
});

test("the X means Rifiuta", async ({ page }) => {
  const hits = await watchGoogle(page);
  await page.goto("index.html");
  await banner(page).getByRole("button", { name: /Chiudi: rifiuta/ }).click();
  await expect(banner(page)).toHaveCount(0);
  expect((await saved(page)).choice).toBe("denied");
  expect(hits).toEqual([]);
});

test("a choice older than 6 months or of an old policy version is asked again", async ({ browser, baseURL }) => {
  const sevenMonths = Date.now() - 213 * 24 * 3600 * 1000;
  for (const state of [decided(baseURL, "denied", sevenMonths), decided(baseURL, "granted", Date.now(), "old")]) {
    const ctx = await browser.newContext({ storageState: state });
    const page = await ctx.newPage();
    const hits = await watchGoogle(page);
    await page.goto(baseURL + "index.html");
    await expect(banner(page)).toBeVisible();
    expect(hits).toEqual([]);
    await ctx.close();
  }
});

test("Rifiuta and Accetta have the same size and look", async ({ page }) => {
  await page.goto("index.html");
  const no = banner(page).getByRole("button", { name: "Rifiuta", exact: true });
  const yes = banner(page).getByRole("button", { name: "Accetta", exact: true });
  const [a, b] = [await no.boundingBox(), await yes.boundingBox()];
  expect(Math.abs(a.width - b.width)).toBeLessThanOrEqual(1);
  expect(Math.abs(a.height - b.height)).toBeLessThanOrEqual(1);
  const style = (l) =>
    l.evaluate((e) => {
      const s = getComputedStyle(e);
      return [s.color, s.backgroundColor, s.fontSize, s.fontWeight, s.borderTopWidth, s.borderTopColor];
    });
  expect(await style(no)).toEqual(await style(yes));
});

test("usable at 360px: inside the screen, no horizontal scroll", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 640 });
  await page.goto("contact.html");
  const box = await banner(page).boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(360);
  expect(box.y + box.height).toBeLessThanOrEqual(640);
  for (const name of ["Rifiuta", "Accetta"]) {
    await expect(banner(page).getByRole("button", { name, exact: true })).toBeInViewport({ ratio: 1 });
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
});

test("keyboard: first tab stops are in the banner, Enter decides, Escape rejects", async ({ page }) => {
  await page.goto("index.html");
  const focused = () => page.evaluate(() => document.activeElement.textContent.trim());
  const order = [];
  for (let i = 0; i < 4; i++) {
    await page.keyboard.press("Tab");
    order.push(await focused());
  }
  expect(order).toEqual(["×", "Informativa cookie", "Rifiuta", "Accetta"]);
  await page.keyboard.press("Enter");
  await expect(banner(page)).toHaveCount(0);
  expect((await saved(page)).choice).toBe("granted");

  await page.getByRole("link", { name: "Preferenze cookie" }).focus();
  await page.keyboard.press("Enter");
  await expect(banner(page)).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(banner(page)).toHaveCount(0);
  expect((await saved(page)).choice).toBe("denied");
  await expect(page.getByRole("link", { name: "Preferenze cookie" })).toBeFocused();
});

test("revoking after Accetta stops GA and deletes the _ga cookies", async ({ page, baseURL }) => {
  await watchGoogle(page);
  await page.goto("index.html");
  await banner(page).getByRole("button", { name: "Accetta", exact: true }).click();
  const host = new URL(baseURL).hostname;
  await page.context().addCookies([
    { name: "_ga", value: "GA1.1.1.1", domain: host, path: "/" },
    { name: "_ga_TVGN1XBX7H", value: "GS1.1.1", domain: host, path: "/" },
    { name: "other", value: "keep", domain: host, path: "/" },
  ]);
  await page.getByRole("link", { name: "Preferenze cookie" }).click();
  await expect(banner(page)).toContainText("Scelta attuale: statistiche accettate.");
  await banner(page).getByRole("button", { name: "Rifiuta", exact: true }).click();
  expect(await gaCookies(page)).toEqual([]);
  expect((await page.context().cookies()).map((c) => c.name)).toContain("other");
  expect((await consentCalls(page)).at(-1)).toEqual(["update", { analytics_storage: "denied" }]);
  expect(await page.evaluate(() => window["ga-disable-G-TVGN1XBX7H"])).toBe(true);
});

test.describe("every page", () => {
  // a saved "Rifiuta", as in the config
  test.use({ storageState: async ({ baseURL }, use) => use(decided(baseURL)) });

  for (const path of PAGES.concat(["crucidev/privacy/index.html"])) {
    test(`${path}: no Google before consent, "Preferenze cookie" reopens the banner`, async ({ page }) => {
      const hits = await watchGoogle(page);
      await page.goto(path);
      await expect(banner(page)).toHaveCount(0);
      const footer = page.locator("footer");
      await expect(footer.getByRole("link", { name: "Privacy", exact: true })).toHaveAttribute("href", /privacy\.html$/);
      await footer.getByRole("link", { name: "Preferenze cookie" }).click();
      await expect(banner(page)).toBeVisible();
      await expect(banner(page)).toBeFocused();
      expect(page.url()).not.toContain("#cookie");
      expect(hits).toEqual([]);
    });
  }
});
