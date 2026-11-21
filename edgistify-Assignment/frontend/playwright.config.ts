import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

const backendDir = fileURLToPath(new URL("../backend", import.meta.url));
const dbPath = process.env.E2E_DB_PATH ?? path.join(os.tmpdir(), `edgistify-e2e-${process.pid}.db`);

for (const suffix of ["", "-wal", "-shm"]) {
  fs.rmSync(`${dbPath}${suffix}`, { force: true });
}

process.env.DB_PATH = dbPath;
process.env.PORT = process.env.E2E_PORT ?? "3000";
process.env.JWT_SECRET ??= "playwright-e2e-jwt-secret";
process.env.VITE_API_URL = `http://127.0.0.1:${process.env.PORT}/api`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: process.env.CI ? 1 : 2,
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["junit", { outputFile: "test-results/junit.xml" }],
  ],
  outputDir: "test-results/artifacts",
  use: {
    ...devices["Desktop Chrome"],
    baseURL: "http://127.0.0.1:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    viewport: { width: 1440, height: 900 },
  },
  webServer: [
    {
      command: "npm run seed && npm start",
      cwd: backendDir,
      url: `http://127.0.0.1:${process.env.PORT}/`,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        DB_PATH: dbPath,
        PORT: process.env.PORT,
        JWT_SECRET: process.env.JWT_SECRET,
      },
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5173 --strictPort",
      url: "http://127.0.0.1:5173/",
      reuseExistingServer: false,
      timeout: 120_000,
      env: { VITE_API_URL: process.env.VITE_API_URL },
    },
  ],
});
