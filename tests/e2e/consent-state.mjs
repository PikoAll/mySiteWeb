// A saved "Rifiuta" for the other specs, so the cookie banner does not cover
// what they test. consent.spec.mjs starts from an empty browser instead.
import { readFileSync } from "fs";

const JS = readFileSync(new URL("../../scripts/consent.js", import.meta.url), "utf8");
export const VERSION = JS.match(/var VERSION = "([^"]+)"/)[1];
export const KEY = "pikobit-consent";

export const decided = (baseURL, choice = "denied", ts = Date.now(), version = VERSION) => ({
  cookies: [],
  origins: [
    {
      origin: new URL(baseURL).origin,
      localStorage: [{ name: KEY, value: JSON.stringify({ choice, version, ts }) }],
    },
  ],
});
