// Headless only. Uses the server already on :8000 (python3 -m http.server
// from the repo root) or starts one. Run: cd tests/e2e && npm ci && npx playwright test
import { defineConfig } from "@playwright/test";

const PORT = process.env.PORT || 8000;

export default defineConfig({
  testDir: ".",
  timeout: 60_000,
  workers: 4,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${PORT}/`, headless: true },
  webServer: {
    command: `python3 -m http.server ${PORT} --directory ../..`,
    url: `http://localhost:${PORT}/index.html`,
    reuseExistingServer: true,
  },
});
