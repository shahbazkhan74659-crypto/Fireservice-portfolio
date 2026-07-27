import { test, expect } from '@playwright/test';
import { E2E_MARKER } from './helpers/constants';

// Contact is the representative form here — Survey/Consultation share the
// exact same island pattern (idle|submitting|success|error state machine,
// Zod client-side + DRF server-side validation) documented in CLAUDE.md, so
// one full submission end-to-end is enough to catch a broken pattern without
// tripling this file for near-identical coverage.
test('contact form: validation error, then a real submission succeeds', async ({ page }) => {
  await page.goto('/contact/');

  const form = page.locator('form.contact__form');
  await expect(form.getByRole('button', { name: 'Submit Enquiry' })).toBeVisible();

  // Empty submit — client-side (Zod) validation should block it and show
  // at least one inline field error, not silently no-op or hit the network.
  await form.getByRole('button', { name: 'Submit Enquiry' }).click();
  await expect(form.locator('.form-note').first()).toBeVisible();

  await page.locator('#name').fill(E2E_MARKER);
  await page.locator('#phone').fill('9876543210');
  await page.locator('#email').fill('e2e-test@example.com');
  await page.locator('#service').selectOption('fire_detection');
  await page.locator('#message').fill('Automated end-to-end test submission — safe to ignore.');

  await form.getByRole('button', { name: 'Submit Enquiry' }).click();

  await expect(page.getByRole('heading', { name: 'Thank You' })).toBeVisible({ timeout: 10000 });
  await expect(page.getByText(/received/i)).toBeVisible();
});
