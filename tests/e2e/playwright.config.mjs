// Headless only. Uses the server already on :8000 (python3 -m http.server
// from the repo root) or starts one. Run: cd tests/e2e && npm ci && npx playwright test
import { defineConfig } from "@playwright/test";
import { decided } from "./consent-state.mjs";

const PORT = process.env.PORT || 8000;
const BASE = `http://localhost:${PORT}/`;

export default defineConfig({
  testDir: ".",
  timeout: 60_000,
  workers: 4,
  // The first page of brand.spec can stall on "networkidle" while the 4
  // workers cold-start against the single python server; a real failure
  // (404, retired image) fails every attempt, so a retry hides only the stall.
  retries: 2,
  reporter: [["list"]],
  use: { baseURL: BASE, headless: true, storageState: decided(BASE) },
  webServer: {
    command: `python3 -m http.server ${PORT} --directory ../..`,
    url: `http://localhost:${PORT}/index.html`,
    reuseExistingServer: true,
  },
});
