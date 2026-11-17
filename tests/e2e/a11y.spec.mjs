// Automatic accessibility check (axe-core): no serious or critical violation
// on any page, except the few documented in a11y-eccezioni.json.
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "fs";
import { PAGES } from "./pages.mjs";

const ECCEZIONI = JSON.parse(readFileSync(new URL("./a11y-eccezioni.json", import.meta.url), "utf8"));

test("le eccezioni sono al massimo 5 e hanno un motivo", () => {
  expect(ECCEZIONI.length).toBeLessThanOrEqual(5);
  for (const e of ECCEZIONI) expect(e.motivo?.trim()).toBeTruthy();
});

for (const page of PAGES) {
  test(`a11y ${page}`, async ({ page: p }) => {
    // No motion: the scroll-reveal sections must be in their final state,
    // not mid-fade, or axe measures a blended colour.
    await p.emulateMedia({ reducedMotion: "reduce" });
    await p.goto(page);
    await p.evaluate(() => document.querySelectorAll(".reveal").forEach((e) => e.classList.add("is-visible")));
    const { violations } = await new AxeBuilder({ page: p }).analyze();
    const gravi = violations
      .filter((v) => ["serious", "critical"].includes(v.impact))
      .filter((v) => !ECCEZIONI.some((e) => e.regola === v.id && (!e.pagina || e.pagina === page)));
    expect(
      gravi.map((v) => `${v.id} (${v.impact}): ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`),
    ).toEqual([]);
  });
}
