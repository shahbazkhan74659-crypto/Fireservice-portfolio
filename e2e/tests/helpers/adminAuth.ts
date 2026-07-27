import type { Page } from '@playwright/test';
import { E2E_PASSWORD, E2E_USERNAME } from './constants';

// Logs in through the real UI (not a cookie/storageState shortcut) so every
// admin spec also incidentally exercises the login form — deliberate for a
// suite this size, where a handful of full-flow tests are worth more than
// saving a couple seconds per test file.
export async function loginAsAdmin(page: Page) {
  await page.goto('/admin-hub/');
  await page.locator('#username').fill(E2E_USERNAME);
  await page.locator('#password').fill(E2E_PASSWORD);
  await page.getByRole('button', { name: 'Log In' }).click();
  await page.waitForURL('**/admin-hub/home/');
}
