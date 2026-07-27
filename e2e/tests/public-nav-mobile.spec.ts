import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test('mobile drawer: opens with logo + links, closes on link click', async ({ page }) => {
  await page.goto('/');

  const nav = page.locator('#nav');
  const toggle = page.locator('#navToggle');
  const overlay = page.locator('#navOverlay');

  await expect(nav).not.toHaveClass(/open/);

  await toggle.click();
  await expect(nav).toHaveClass(/open/);
  await expect(overlay).toHaveClass(/open/);
  await expect(nav.locator('.nav__brand')).toBeVisible();
  await expect(nav.locator('a', { hasText: 'Certifications' })).toBeVisible();

  await nav.locator('a', { hasText: 'Certifications' }).click();
  await expect(page).toHaveURL(/\/certifications\/$/);
  await expect(nav).not.toHaveClass(/open/);
});

test('mobile drawer: closes on overlay click without navigating', async ({ page }) => {
  await page.goto('/');

  await page.locator('#navToggle').click();
  await expect(page.locator('#nav')).toHaveClass(/open/);

  // Click well below the fixed header — it sits on top of the overlay in
  // that top strip (higher z-index) and would intercept the click there.
  await page.locator('#navOverlay').click({ position: { x: 20, y: 400 } });
  await expect(page.locator('#nav')).not.toHaveClass(/open/);
  await expect(page).toHaveURL('/');
});

test('mobile drawer: X stays put when a scroll event fires while open', async ({ page }) => {
  // Regression test for the "close cross moves upward while scrolling"
  // bug — stray scroll events while nav-open used to shrink the header
  // (topbar collapse) and drag the X with it.
  await page.goto('/');
  await page.locator('#navToggle').click();
  await expect(page.locator('#nav')).toHaveClass(/open/);

  const before = await page.locator('#navToggle').boundingBox();
  await page.evaluate(() => {
    window.scrollTo(0, 50);
    window.dispatchEvent(new Event('scroll'));
  });
  await page.waitForTimeout(200);
  const after = await page.locator('#navToggle').boundingBox();

  expect(after?.y).toBe(before?.y);
});
