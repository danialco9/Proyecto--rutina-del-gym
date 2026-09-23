import { defineConfig, devices } from '@playwright/test'

// The whole stack, as `docker compose up` serves it: nginx, the API and PostgreSQL.
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:8080'

export default defineConfig({
  testDir: './tests',
  // The app is used on a gym floor, one-handed, so the suite runs on a phone-sized screen.
  use: { baseURL, trace: 'on-first-retry', locale: 'es-ES', timezoneId: 'Europe/Madrid' },
  expect: { timeout: 10_000 },
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list']],
  projects: [{ name: 'mobile', use: { ...devices['Pixel 7'] } }],
})
