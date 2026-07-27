import { defineConfig, devices } from '@playwright/test';

// This suite targets an already-running dev stack (Django + Vite) rather
// than starting its own servers — see README.md for why (mainly: Vite's
// dev server is what makes the React islands work at all in dev, and
// juggling two `webServer` processes reliably across platforms wasn't
// worth it for a suite this size). global-setup.ts fails fast with a clear
// message if either server isn't reachable.
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'html',
  globalSetup: require.resolve('./global-setup.ts'),
  globalTeardown: require.resolve('./global-teardown.ts'),
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
