import { test, expect } from '@playwright/test';
import { E2E_PASSWORD, E2E_USERNAME } from './helpers/constants';

test('protected pages redirect to login when logged out', async ({ page }) => {
  await page.goto('/admin-hub/home/');
  await expect(page).toHaveURL(/\/admin-hub\/\?next=/);
});

test('wrong credentials show an inline error and do not log in', async ({ page }) => {
  await page.goto('/admin-hub/');
  await page.locator('#username').fill(E2E_USERNAME);
  await page.locator('#password').fill('definitely-wrong-password');
  await page.getByRole('button', { name: 'Log In' }).click();

  await expect(page.locator('.form-note')).toBeVisible();
  await expect(page).toHaveURL(/\/admin-hub\/$/);
});

test('correct credentials log in, and Log Out re-gates the dashboard', async ({ page }) => {
  await page.goto('/admin-hub/');
  await page.locator('#username').fill(E2E_USERNAME);
  await page.locator('#password').fill(E2E_PASSWORD);
  await page.getByRole('button', { name: 'Log In' }).click();

  await page.waitForURL('**/admin-hub/home/');
  await expect(page.getByText('Admin Hub')).toBeVisible();

  await page.getByRole('button', { name: 'Log Out' }).click();
  await expect(page).toHaveURL(/\/admin-hub\/$/);

  // Confirms the session was actually destroyed, not just a client-side redirect.
  await page.goto('/admin-hub/home/');
  await expect(page).toHaveURL(/\/admin-hub\/\?next=/);
});
