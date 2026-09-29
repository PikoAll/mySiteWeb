// Details that make new sections look like the rest of the site: same
// headings, one-line pills of equal height, one-line page index, footer
// link that never breaks in the middle.
import { test, expect } from "@playwright/test";

const styleOf = (loc) =>
  loc.evaluate((el) => {
    const s = getComputedStyle(el);
    const bar = getComputedStyle(el, "::after");
    return { color: s.color, size: s.fontSize, bar: bar.content !== "none" && bar.height };
  });

const lineCount = (loc) =>
  loc.evaluate((el) => {
    const r = document.createRange();
    r.selectNodeContents(el);
    return new Set([...r.getClientRects()].map((c) => Math.round(c.top))).size;
  });

for (const width of [1366, 390]) {
  test.describe(`${width}px`, () => {
    test.use({ viewport: { width, height: 900 } });

    test("home: 'Dove lavoro' looks like the other home sections", async ({ page }) => {
      await page.goto("index.html");
      const h2 = page.locator("#dove-lavoro > h2");
      expect(await styleOf(h2)).toEqual(await styleOf(page.locator("#servizi > h2")));
      const lead = page.locator("#dove-lavoro > p").first();
      const ref = page.locator("#servizi .block-cta");
      const w = async (l) => l.evaluate((el) => getComputedStyle(el).maxWidth);
      expect(await w(lead)).toBe(await w(ref));
      const pills = page.locator("#dove-lavoro .city-grid li");
      const heights = await pills.evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().height)));
      expect(new Set(heights).size, `pill heights ${heights}`).toBe(1);
      if (width >= 1024)
        for (const a of await pills.locator("a").all()) expect(await lineCount(a), await a.textContent()).toBe(1);
      // the text sits in the middle of the pill
      const off = await pills.first().evaluate((li) => {
        const a = li.querySelector("a").getBoundingClientRect();
        const b = li.getBoundingClientRect();
        return Math.abs(a.top - b.top - (b.bottom - a.bottom));
      });
      expect(off).toBeLessThanOrEqual(2);
    });

    test("footer: the Google Maps link never breaks", async ({ page }) => {
      await page.goto("about.html");
      const a = page.locator('footer a[href^="https://www.google.com/maps"]');
      expect(await lineCount(a)).toBe(1);
    });

    test("dove-lavoro: Turi is in the Sud-est barese group", async ({ page }) => {
      await page.goto("dove-lavoro.html");
      const group = page.locator("section.goals", { has: page.locator("h2", { hasText: "Sud-est barese" }) });
      await expect(group.locator('.city-grid a[href="programmatore-turi.html"]')).toHaveCount(1);
      const cols = await group.locator(".city-grid li").evaluateAll((els) =>
        Math.max(...Object.values(els.reduce((m, e) => {
          const t = Math.round(e.getBoundingClientRect().top);
          m[t] = (m[t] || 0) + 1;
          return m;
        }, {}))));
      // one column only on phones (no name on two lines), rows from 480px
      if (width >= 480) expect(cols, "never a single column").toBeGreaterThan(1);
      await expect(page.locator("section.goals h2", { hasText: /^Turi$/ })).toHaveCount(0);
    });
  });
}

test.describe("1366px", () => {
  test.use({ viewport: { width: 1366, height: 900 } });
  test("websites: the page index fits on one line", async ({ page }) => {
    await page.goto("websites.html");
    const tops = await page.locator(".page-toc li").evaluateAll((els) =>
      new Set(els.map((e) => Math.round(e.getBoundingClientRect().top))).size);
    expect(tops).toBe(1);
  });
});

const aloneArrows = (p) =>
  p.$$eval(".city-grid li.card--link a", (els) =>
    els.filter((a) => {
      const r = document.createRange();
      r.selectNodeContents(a);
      // the link's first line box starts with the ::before arrow
      const linkTop = a.getClientRects()[0].top;
      const textTop = Math.min(...[...r.getClientRects()].map((c) => c.top));
      return textTop > linkTop + 2;
    }).map((a) => a.textContent.trim()));

test.describe("390px arrows", () => {
  test.use({ viewport: { width: 390, height: 900 } });
  for (const page of ["index.html", "dove-lavoro.html", "programmatore-bari.html"])
    test(`the pill arrow never sits alone on a line: ${page}`, async ({ page: p }) => {
      await p.goto(page);
      expect(await aloneArrows(p)).toEqual([]);
    });

  test("the check does see a lonely arrow (old breakable arrow, 2 columns)", async ({ page: p }) => {
    await p.goto("index.html");
    await p.addStyleTag({ content: `
      .city-grid li.card--link a::before { content: "→ " }
      #dove-lavoro .city-grid { --cols: 2 }` });
    expect(await aloneArrows(p)).toContain("Casamassima");
  });
});

// A pill name goes on two lines only on phones, never where there is room.
const wrappedPills = (p) =>
  p.$$eval(".city-grid li a", (els) =>
    els.filter((a) => {
      const r = document.createRange();
      r.selectNodeContents(a);
      return new Set([...r.getClientRects()].map((c) => Math.round(c.top))).size > 1;
    }).map((a) => a.textContent.trim()));

for (const width of [768, 1024, 1366]) {
  test.describe(`${width}px pills`, () => {
    test.use({ viewport: { width, height: 900 } });
    const pages = ["dove-lavoro.html", "index.html", "programmatore-monopoli.html"]
      .concat(width >= 1024 ? ["programmatore-bari.html", "programmatore-conversano.html", "programmatore-ostuni.html"] : []);
    for (const page of pages)
      test(`no pill on two lines: ${page}`, async ({ page: p }) => {
        await p.goto(page);
        expect(await wrappedPills(p)).toEqual([]);
      });

    test("dove-lavoro: every group has pills of the same height", async ({ page: p }) => {
      await p.goto("dove-lavoro.html");
      const h = await p.$$eval("main .city-grid li", (els) => [...new Set(els.map((e) => Math.round(e.getBoundingClientRect().height)))]);
      expect(h.length, `heights ${h}`).toBe(1);
    });
  });
}

for (const width of [1366, 390]) {
  test.describe(`${width}px Monopoli zones`, () => {
    test.use({ viewport: { width, height: 900 } });
    test("Monopoli 'Zone in cui lavoro' is the home 'Dove lavoro' component", async ({ page: p }) => {
      await p.goto("index.html");
      const home = await styleOf(p.locator("#dove-lavoro > h2"));
      await p.goto("programmatore-monopoli.html");
      const sec = p.locator("section.block.goals", { has: p.locator("h2", { hasText: "Zone in cui lavoro" }) });
      await expect(sec).toHaveCount(1);
      expect(await styleOf(sec.locator("> h2"))).toEqual(home);
      await expect(sec.locator(".city-grid li")).toHaveCount(12);
    });
  });
}

for (const [width, rows] of [[390, [1, 1, 1, 1, 1, 1, 1]], [480, [1, 2, 2, 2]], [768, [1, 3, 3]], [1366, [4, 3]]]) {
  test.describe(`${width}px Sud-est barese rows`, () => {
    test.use({ viewport: { width, height: 900 } });
    test(`rows ${rows.join("+")}, Monopoli first`, async ({ page: p }) => {
      await p.goto("dove-lavoro.html");
      const grid = p.locator("section.goals", { has: p.locator("h2", { hasText: "Sud-est barese" }) }).locator(".city-grid");
      const got = await grid.locator("li").evaluateAll((els) => {
        const m = new Map();
        for (const e of els) { const t = Math.round(e.getBoundingClientRect().top); m.set(t, (m.get(t) || 0) + 1); }
        return [...m.keys()].sort((a, b) => a - b).map((k) => m.get(k));
      });
      expect(got).toEqual(rows);
    });
  });
}

test.describe("390px dove-lavoro pills", () => {
  test.use({ viewport: { width: 390, height: 900 } });
  test("every pill on one line, same height in every group", async ({ page: p }) => {
    await p.goto("dove-lavoro.html");
    expect(await wrappedPills(p)).toEqual([]);
    const h = await p.$$eval("main .city-grid li", (els) => [...new Set(els.map((e) => Math.round(e.getBoundingClientRect().height)))]);
    expect(h.length, `heights ${h}`).toBe(1);
  });
});

// "Zone vicine" of the city pages: the short last row sits in the middle,
// and on phones the pills keep one line.
const lastRowOffset = (p) =>
  p.locator("section:has(> h2:text-is('Zone vicine')) .city-grid").evaluate((ul) => {
    const items = [...ul.children].map((li) => li.getBoundingClientRect());
    const lastTop = Math.max(...items.map((r) => Math.round(r.top)));
    const last = items.filter((r) => Math.round(r.top) === lastTop);
    const box = ul.getBoundingClientRect();
    const first = items.filter((r) => Math.round(r.top) === Math.round(items[0].top));
    const rowLeft = Math.min(...first.map((r) => r.left)), rowRight = Math.max(...first.map((r) => r.right));
    const left = Math.min(...last.map((r) => r.left)) - rowLeft;
    const right = rowRight - Math.max(...last.map((r) => r.right));
    return Math.abs(left - right);
  });

for (const page of ["programmatore-bari.html", "programmatore-conversano.html", "programmatore-ostuni.html"]) {
  test.describe(`1366px zone vicine ${page}`, () => {
    test.use({ viewport: { width: 1366, height: 900 } });
    test("the last row is centred", async ({ page: p }) => {
      await p.goto(page);
      expect(await lastRowOffset(p)).toBeLessThanOrEqual(2);
    });
  });
  test.describe(`390px zone vicine ${page}`, () => {
    test.use({ viewport: { width: 390, height: 900 } });
    test("no pill on two lines", async ({ page: p }) => {
      await p.goto(page);
      expect(await wrappedPills(p)).toEqual([]);
    });
  });
}
