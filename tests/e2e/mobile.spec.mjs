// Phone viewport: the hamburger menu opens and leads to the contact page,
// and no fixed page scrolls sideways.
import { test, expect } from "@playwright/test";
import { PAGES } from "./pages.mjs";

test.use({ viewport: { width: 375, height: 667 }, hasTouch: true, isMobile: true });

test("phone: the menu opens and reaches the contact page", async ({ page }) => {
  await page.goto("index.html");
  const burger = page.locator("#hamburger-menu");
  await expect(burger).toBeVisible();
  await burger.click();
  await expect(page.locator("#navbar")).toHaveClass(/active/);
  const link = page.locator("#navbar .nav-cta a[href='contact.html']");
  await expect(link).toBeVisible();
  await link.click();
  await expect(page).toHaveURL(/contact\.html$/);
  await expect(page.locator("main")).toBeVisible();
});

for (const name of PAGES) {
  test(`phone: no horizontal scroll on ${name}`, async ({ page }) => {
    await page.goto(name);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - innerWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);
  });
}
