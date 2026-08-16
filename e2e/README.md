# End-to-end tests

Playwright suite covering the public site and Admin Hub. This runs against
your **already-running dev servers** rather than starting its own — it does
not spin up a separate test database, so it uses `core/management/commands/e2e_data.py`
to create one throwaway admin account (`e2e_admin`) and marker-tagged rows
(prefixed `E2E Test Runner`) before the run, and delete them afterward
(`global-setup.ts` / `global-teardown.ts`). Don't run this against a database
you can't afford to have briefly gain a test admin account and a few test leads.

## Before running

Both dev servers must already be up:

```bash
# from the repo root, in one terminal
venv\Scripts\activate  (or: source venv/Scripts/activate)
python manage.py runserver

# in another terminal
cd frontend
npm run dev
```

`global-setup.ts` checks both `http://localhost:8000/` and `http://localhost:5173/`
before running anything and fails immediately with a clear message if either
is unreachable — you don't need to guess which test is timing out and why.

## Install (first time only)

```bash
cd e2e
npm install
npx playwright install chromium
```

## Run

```bash
cd e2e
npm test            # headless
npm run test:headed # watch it click through the browser
npm run test:ui     # Playwright's interactive UI mode
npm run report      # open the HTML report from the last run
```

## What's covered

- `public-pages.spec.ts` — every public route resolves and renders its
  heading; desktop nav links work; active-link highlighting.
- `public-forms.spec.ts` — the contact form's client-side validation and a
  real end-to-end submission (Survey/Consultation share the same island
  pattern, so this one form stands in for all three).
- `public-nav-mobile.spec.ts` — the mobile drawer: opens/closes, link click
  navigates and closes it, overlay click closes without navigating, and a
  regression check that the close (X) button doesn't drift on scroll.
- `admin-auth.spec.ts` — logged-out redirect to login, wrong-credentials
  error, and a full login → logout → re-gated cycle.
- `admin-nav-mobile.spec.ts` — the Admin Hub drawer: logo above the links,
  username + Log Out pinned to the bottom, and logging out from there.
- `admin-crud.spec.ts` — add then delete a Client Logo through the real
  Add/Delete modals (Products/Services etc. share the identical pattern, so
  this one model stands in for all of them).

This is a "minimal e2e suite" per the project's stated test strategy in
CLAUDE.md — a handful of full, real user flows, not exhaustive per-page or
per-model coverage. pytest-django/Vitest are meant to carry the bulk of test
coverage; nothing in that direction exists yet either (see CLAUDE.md's "Not
started yet" section).

## Not covered (yet)

Every other admin-managed content type (Client Logos, Products, Services,
Fire Risk Assessment items, Mission & Vision, Certifications, site-setting
stats), Leads page tabs/detail modals, Counter-page-style dashboards, and
the Survey/Consultation forms specifically (they share Contact's pattern —
see above). Extend by copying `admin-crud.spec.ts`'s shape for another
model, or `public-forms.spec.ts`'s shape for another form.
