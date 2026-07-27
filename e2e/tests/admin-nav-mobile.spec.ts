import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers/adminAuth';

test.use({ viewport: { width: 375, height: 812 } });

test('admin drawer: logo above links, username + Log Out pinned at the bottom', async ({ page }) => {
  await loginAsAdmin(page);

  const nav = page.locator('#adminNav');
  await expect(nav).not.toHaveClass(/open/);

  await page.locator('#adminNavToggle').click();
  await expect(nav).toHaveClass(/open/);

  // Logo sits above the links (DOM order = visual order here, both normal-
  // flow children of the same column-direction .nav).
  const brandBox = await nav.locator('.nav__brand').boundingBox();
  const homeLinkBox = await nav.locator('a', { hasText: 'Home' }).boundingBox();
  expect(brandBox!.y).toBeLessThan(homeLinkBox!.y);

  await expect(nav.locator('a', { hasText: 'Leads' })).toBeVisible();
  await expect(nav.locator('a', { hasText: 'Clientele' })).toBeVisible();
  await expect(nav.locator('a', { hasText: 'Services' })).toBeVisible();
  await expect(nav.locator('a', { hasText: 'Certifications' })).toBeVisible();

  // Footer (username + Log Out) pinned to the bottom of the drawer, below
  // every link — this is the whole point of margin-top:auto on .nav__footer.
  const footer = nav.locator('.nav__footer');
  await expect(footer).toBeVisible();
  await expect(footer.getByText('e2e_admin')).toBeVisible();
  const footerBox = await footer.boundingBox();
  const lastLinkBox = await nav.locator('a', { hasText: 'Certifications' }).boundingBox();
  expect(footerBox!.y).toBeGreaterThan(lastLinkBox!.y);
});

test('admin drawer: Log Out from the drawer footer actually logs out', async ({ page }) => {
  await loginAsAdmin(page);
  await page.locator('#adminNavToggle').click();

  await page.locator('#adminNav .nav__footer').getByRole('button', { name: 'Log Out' }).click();
  await expect(page).toHaveURL(/\/admin-hub\/$/);

  await page.goto('/admin-hub/home/');
  await expect(page).toHaveURL(/\/admin-hub\/\?next=/);
});
