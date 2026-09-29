// Brand and technical SEO on EVERY page (blog included): no local request
// fails, the retired images are never loaded, favicon/manifest/og:image are
// reachable and the social preview is 1200x630.
import { test, expect } from "@playwright/test";
import { readdirSync } from "fs";
import { fileURLToPath } from "url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const ALL_PAGES = readdirSync(ROOT).filter((f) => f.endsWith(".html"))
  .concat(readdirSync(ROOT + "blog").filter((f) => f.endsWith(".html")).map((f) => "blog/" + f))
  .concat(["crucidev/privacy/"])
  .sort();
const RETIRED = /\/images\/(filigrana|banner|logo)\.webp/;
const SITE = "https://pikobit.it/";

for (const page of ALL_PAGES) {
  test(`no failed or retired requests: ${page}`, async ({ page: p, baseURL }) => {
    const failed = [];
    const retired = [];
    p.on("response", (r) => {
      if (!r.url().startsWith(baseURL)) return;
      if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`);
    });
    p.on("request", (r) => { if (RETIRED.test(r.url())) retired.push(r.url()); });
    await p.goto(page, { waitUntil: "load" });
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await p.waitForLoadState("networkidle");
    expect(failed).toEqual([]);
    expect(retired).toEqual([]);
  });
}

test("favicon set, manifest and og:image are reachable", async ({ page: p, request }) => {
  await p.goto("index.html");
  const links = await p.$$eval(
    'link[rel="icon"], link[rel="apple-touch-icon"], link[rel="manifest"]',
    (els) => els.map((e) => e.getAttribute("href")),
  );
  expect(links).toEqual(expect.arrayContaining([
    "/favicon.ico", "/images/brand/favicon-32.png", "/images/brand/favicon-192.png",
    "/apple-touch-icon.png", "/site.webmanifest",
  ]));
  for (const href of links) expect((await request.get(href)).status(), href).toBe(200);

  const manifest = await (await request.get("/site.webmanifest")).json();
  for (const icon of manifest.icons) expect((await request.get(icon.src)).status(), icon.src).toBe(200);

  const og = await p.getAttribute('meta[property="og:image"]', "content");
  expect(og.startsWith(SITE)).toBe(true);
  const local = "/" + og.slice(SITE.length);
  expect((await request.get(local)).status()).toBe(200);
  const size = await p.evaluate(async (src) => {
    const img = new Image();
    img.src = src;
    await img.decode();
    return [img.naturalWidth, img.naturalHeight];
  }, local);
  expect(size).toEqual([1200, 630]);
});

test("IndexNow key file is served from the site root", async ({ request }) => {
  const key = readdirSync(ROOT).find((f) => /^[0-9a-f]{32}\.txt$/.test(f));
  expect(key).toBeTruthy();
  const res = await request.get("/" + key);
  expect(res.status()).toBe(200);
  expect((await res.text()).trim()).toBe(key.replace(".txt", ""));
});

test("structured data parses in the browser on every page", async ({ page: p }) => {
  for (const page of ALL_PAGES) {
    await p.goto(page, { waitUntil: "domcontentloaded" });
    const blocks = await p.$$eval('script[type="application/ld+json"]', (els) => els.map((e) => e.textContent));
    expect(blocks.length, page).toBe(1);
    expect(() => JSON.parse(blocks[0]), page).not.toThrow();
  }
});
