import path from 'node:path';
import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers/adminAuth';
import { E2E_MARKER } from './helpers/constants';

// Brand is the representative content type here — Client Logos/Products
// share the exact same model -> serializer -> API -> React-island-with-
// Modal pattern (documented in CLAUDE.md), so one full Add+Delete cycle is
// enough to catch a broken pattern without repeating this file six times
// for near-identical coverage.
test('admin: add a Brand, see it in the grid, then delete it', async ({ page }) => {
  const brandName = `${E2E_MARKER} Brand`;

  await loginAsAdmin(page);
  await page.goto('/admin-hub/clientele/');

  // Scoped to #admin-brands-root: the same page also mounts an
  // admin-client-logos island built from an identical Add/Modal pattern
  // (same "+ Add" button text, same .client-logos__admin-actions class),
  // so an unscoped locator would match two buttons.
  const brandsRoot = page.locator('#admin-brands-root');
  await brandsRoot.getByRole('button', { name: '+ Add' }).click();

  await page.locator('#new-brand-name').fill(brandName);
  await page.locator('#new-brand-file').setInputFiles(path.join(__dirname, '..', 'fixtures', 'test-logo.png'));
  await page.getByRole('button', { name: 'Add Brand' }).click();

  const card = brandsRoot.locator('.logo-card--admin').filter({ has: page.locator(`img[alt="${brandName}"]`) });
  await expect(card).toBeVisible({ timeout: 10000 });

  await card.getByRole('button', { name: 'Delete' }).click();
  await page.getByRole('button', { name: 'Yes, Delete' }).click();

  await expect(brandsRoot.locator(`img[alt="${brandName}"]`)).toHaveCount(0);
});
