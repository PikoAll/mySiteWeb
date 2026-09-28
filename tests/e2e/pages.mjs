// The root pages of the site (blog posts share one template, one is enough).
import { readdirSync } from "fs";
import { fileURLToPath } from "url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
export const PAGES = readdirSync(ROOT)
  .filter((f) => f.endsWith(".html"))
  .sort()
  .concat(readdirSync(ROOT + "blog").filter((f) => f.endsWith(".html")).sort().slice(-1).map((f) => "blog/" + f));

export const CITIES = [
  "monopoli", "bari", "polignano-a-mare", "fasano", "conversano",
  "castellana-grotte", "putignano", "casamassima", "ostuni", "brindisi",
  "taranto", "lecce",
];
