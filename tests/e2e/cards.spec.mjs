// Only clickable cards react: orange hover, pointer, "Scopri di più".
import { test, expect } from "@playwright/test";

test.use({ viewport: { width: 1440, height: 900 } });
const ORANGE = "rgb(255, 165, 0)";

test("home: a service card is a link with the orange hover", async ({ page }) => {
  await page.goto("index.html");
  const card = page.locator("#servizi .card--link").first();
  await expect(card).toHaveCSS("cursor", "pointer");
  await card.hover();
  await page.waitForTimeout(400);
  await expect(card).toHaveCSS("border-top-color", ORANGE);
  expect(await card.evaluate((c) => getComputedStyle(c, "::after").content)).toContain("Scopri di più");
  // anywhere on the card opens the page
  const box = await card.boundingBox();
  await page.mouse.click(box.x + 8, box.y + box.height - 8);
  await expect(page).toHaveURL(/websites\.html$/);
});

test("home: keyboard focus on a card looks like the hover", async ({ page }) => {
  await page.goto("index.html");
  await page.locator("#servizi .card--link a").first().focus();
  await expect(page.locator("#servizi .card--link").first()).toHaveCSS("border-top-color", ORANGE);
});

test("home: the 'why Pikobit' cards are flat, no hover", async ({ page }) => {
  await page.goto("index.html");
  const card = page.locator("#perche-pikobit .card").first();
  await expect(card).not.toHaveClass(/card--link/);
  await card.scrollIntoViewIfNeeded();
  await page.waitForTimeout(700);
  await card.hover();
  await page.waitForTimeout(400);
  await expect(card).toHaveCSS("cursor", "auto");
  await expect(card).toHaveCSS("transform", "none");
  expect(await card.evaluate((c) => getComputedStyle(c, "::after").content)).toBe("none");
});

test("ideas: every card title has the same colour", async ({ page }) => {
  await page.goto("ideas.html");
  const colours = await page.$$eval("#idee .card h3", (hs) =>
    hs.map((h) => getComputedStyle(h.querySelector("a") || h).color),
  );
  expect(colours.length).toBe(6);
  expect(new Set(colours).size).toBe(1);
});

test("menu: 'Contatti' stays #ffa500 on the contact page too", async ({ page }) => {
  for (const url of ["index.html", "contact.html"]) {
    await page.goto(url);
    const cta = page.locator("#navbar .nav-cta a");
    await expect(cta).toHaveCSS("background-color", ORANGE);
  }
  await expect(page.locator("#navbar .nav-cta a")).toHaveAttribute("aria-current", "page");
});
