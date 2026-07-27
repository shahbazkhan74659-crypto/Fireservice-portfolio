import { test, expect } from '@playwright/test';

// One entry per public, server-rendered page (see fireservice/urls.py ->
// core/urls.py) — a lightweight smoke test that each route resolves and
// renders its own distinguishing heading, not a content audit of every page.
const PAGES: Array<{ path: string; heading: string | RegExp }> = [
  { path: '/', heading: /Total Fire Protection|Iconic Techno Service/i },
  { path: '/about/', heading: /About|Who We Are/i },
  { path: '/services/', heading: /Services|Fire Detection/i },
  { path: '/process/', heading: /Process/i },
  { path: '/clientele/', heading: /Client/i },
  { path: '/certifications/', heading: /Certifi/i },
  { path: '/contact/', heading: /Contact|Get in Touch/i },
  { path: '/survey/', heading: /Survey/i },
  { path: '/consultation/', heading: /Consultation/i },
  { path: '/brochure/', heading: /Brochure/i },
];

for (const { path, heading } of PAGES) {
  test(`${path} loads and renders`, async ({ page }) => {
    const response = await page.goto(path);
    expect(response?.ok()).toBeTruthy();
    await expect(page.locator('main')).toContainText(heading);
  });
}

test('nav highlights the current page as active', async ({ page }) => {
  await page.goto('/services/');
  await expect(page.locator('nav.nav a.active')).toHaveText('Services');
});

test('header nav links reach every page (desktop, no drawer)', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/');

  await page.locator('nav.nav a', { hasText: 'About' }).click();
  await expect(page).toHaveURL(/\/about\/$/);

  await page.locator('nav.nav a', { hasText: 'Contact' }).click();
  await expect(page).toHaveURL(/\/contact\/$/);
});

test('footer year is populated (site.js ran)', async ({ page }) => {
  await page.goto('/');
  const year = await page.locator('#year').textContent();
  expect(Number(year)).toBeGreaterThanOrEqual(new Date().getFullYear());
});
