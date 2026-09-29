// contact.html: layout, client validation, the WhatsApp and email messages.
import { test, expect } from "@playwright/test";

// Catch the URL the form would open instead of leaving the page.
const capture = (page) =>
  page.evaluate(() => {
    window.__opened = [];
    window.PikoContact.go = (url, via) => window.__opened.push({ url, via });
  });

const fill = async (page) => {
  await page.fill("#cf-nome", "Mario Rossi");
  await page.fill("#cf-telefono", "+39 333 123 4567");
  await page.fill("#cf-email", "mario@example.it");
  await page.selectOption("#cf-tipo", "Sito web");
  await page.fill("#cf-citta", "Fasano");
  await page.fill("#cf-messaggio", "Vorrei un sito per la mia pizzeria & B&B.");
  await page.check("#cf-privacy");
};

test("empty form: clear errors, focus on the first one, nothing opens", async ({ page }) => {
  await page.goto("contact.html");
  await capture(page);
  await page.getByRole("button", { name: "Invia su WhatsApp" }).click();
  await expect(page.locator("#cf-nome-err")).toHaveText("Scrivi il tuo nome.");
  await expect(page.locator("#cf-messaggio-err")).not.toBeEmpty();
  await expect(page.locator("#cf-privacy-err")).not.toBeEmpty();
  await expect(page.locator("#cf-nome")).toHaveAttribute("aria-invalid", "true");
  await expect(page.locator("#cf-nome")).toBeFocused();
  expect(await page.evaluate(() => window.__opened)).toEqual([]);
});

test("wrong email and phone are rejected, optional when empty", async ({ page }) => {
  await page.goto("contact.html");
  await capture(page);
  await fill(page);
  await page.fill("#cf-email", "mario@");
  await page.fill("#cf-telefono", "abc");
  await page.getByRole("button", { name: "Invia email" }).click();
  await expect(page.locator("#cf-email-err")).not.toBeEmpty();
  await expect(page.locator("#cf-telefono-err")).not.toBeEmpty();
  await page.fill("#cf-email", "");
  await page.fill("#cf-telefono", "");
  await page.getByRole("button", { name: "Invia email" }).click();
  expect(await page.evaluate(() => window.__opened.length)).toBe(1);
});

test("WhatsApp: wa.me with every field in the text", async ({ page }) => {
  await page.goto("contact.html");
  await capture(page);
  await fill(page);
  await page.getByRole("button", { name: "Invia su WhatsApp" }).click();
  const [{ url, via }] = await page.evaluate(() => window.__opened);
  expect(via).toBe("whatsapp");
  expect(url.startsWith("https://wa.me/393518891903?text=")).toBe(true);
  const text = decodeURIComponent(url.split("?text=")[1]);
  for (const s of ["Nome: Mario Rossi", "Telefono: +39 333 123 4567", "Email: mario@example.it",
                   "Progetto: Sito web", "Città: Fasano", "pizzeria & B&B"])
    expect(text).toContain(s);
});

test("email: mailto with subject and body, to the footer address", async ({ page }) => {
  await page.goto("contact.html");
  const footerMail = await page.locator('footer .nap a[href^="mailto:"]').getAttribute("href");
  await capture(page);
  await fill(page);
  await page.getByRole("button", { name: "Invia email" }).click();
  const [{ url, via }] = await page.evaluate(() => window.__opened);
  expect(via).toBe("email");
  expect(url.startsWith(footerMail + "?subject=")).toBe(true);
  const q = new URLSearchParams(url.split("?")[1]);
  expect(q.get("subject")).toBe("Richiesta dal sito - Sito web - Mario Rossi");
  expect(q.get("body")).toContain("Città: Fasano");
  expect(q.get("body")).toContain("pizzeria & B&B");
});

test("the privacy link works and the NAP matches the footer", async ({ page }) => {
  await page.goto("contact.html");
  const info = page.locator(".contact-details");
  await expect(info.locator('a[href="tel:+393518891903"]')).toBeVisible();
  await expect(info.locator('a[href="mailto:piko.bit.00@gmail.com"]')).toBeVisible();
  await expect(info.locator('a[href="https://wa.me/393518891903"]')).toBeVisible();
  // Legal basis is art. 6.1.b (pre-contract), not consent: the box only
  // confirms the notice was read.
  await expect(page.locator('label[for="cf-privacy"]')).toHaveText("Ho letto l'informativa privacy. *");
  await expect(page.locator("#cf-privacy")).toHaveAttribute("required", "");
  await page.locator('label[for="cf-privacy"] a').click();
  await expect(page).toHaveURL(/privacy\.html$/);
  await expect(page.locator("h1")).toHaveText("Informativa privacy");
});

for (const [width, side] of [[390, false], [1280, true]]) {
  test(`info and form ${side ? "side by side" : "stacked"} at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("contact.html");
    const a = await page.locator(".contact-details").boundingBox();
    const b = await page.locator(".contact-form").boundingBox();
    if (side) expect(b.x).toBeGreaterThan(a.x + a.width - 1);
    else expect(b.y).toBeGreaterThan(a.y + a.height - 1);
  });
}
