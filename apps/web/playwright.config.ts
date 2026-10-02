import { defineConfig } from "@playwright/test";

/** Requires the API on :8000 (pnpm api:dev). The web server is started here if absent. */
export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    // Optional: reuse a locally installed Chromium instead of `playwright install`.
    launchOptions: process.env.PW_CHROMIUM_PATH
      ? { executablePath: process.env.PW_CHROMIUM_PATH }
      : {},
  },
  webServer: {
    command: "pnpm dev",
    url: "http://127.0.0.1:3000/login",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
