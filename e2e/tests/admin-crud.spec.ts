import path from 'node:path';
import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers/adminAuth';
import { E2E_MARKER } from './helpers/constants';

// Client Logos is the representative content type here — Products/Services/
// etc share the exact same model -> serializer -> API -> React-island-with-
// Modal pattern (documented in CLAUDE.md), so one full Add+Delete cycle is
// enough to catch a broken pattern without repeating this file six times
// for near-identical coverage.
test('admin: add a Client Logo, see it in the grid, then delete it', async ({ page }) => {
  const logoName = `${E2E_MARKER} Client Logo`;

  await loginAsAdmin(page);
  await page.goto('/admin-hub/clientele/');

  const logosRoot = page.locator('#admin-client-logos-root');
  await logosRoot.getByRole('button', { name: '+ Add' }).click();

  await page.locator('#new-logo-name').fill(logoName);
  await page.locator('#new-logo-file').setInputFiles(path.join(__dirname, '..', 'fixtures', 'test-logo.png'));
  await page.getByRole('button', { name: 'Add Logo' }).click();

  const card = logosRoot.locator('.logo-card--admin').filter({ has: page.locator(`img[alt="${logoName}"]`) });
  await expect(card).toBeVisible({ timeout: 10000 });

  await card.getByRole('button', { name: 'Delete' }).click();
  await page.getByRole('button', { name: 'Yes, Delete' }).click();

  await expect(logosRoot.locator(`img[alt="${logoName}"]`)).toHaveCount(0);
});
