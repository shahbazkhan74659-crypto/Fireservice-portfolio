# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Project

Real production build for **Iconic Techno Service (ITS)**, a Silvassa-based fire & life-safety systems company. Real branding is live throughout (name, logo, phones, address, GST, service list) — nothing here is placeholder content anymore.

A static single-page prototype exists at the sibling folder `C:\FireService\` (no `!`) — historical reference only, fully superseded by this build. An original planning doc also exists at `C:\Users\shahb\.claude\plans\curried-greeting-wombat.md`; treat it as historical background too — this file is the up-to-date source of truth.

**Don't use the Chrome browser automation extension unless explicitly told to.**

## Stack & commands

Django 5.2 (server-rendered templates) + PostgreSQL (local dev and prod both, via `django-environ`/`.env` and `psycopg`) + React "islands" in TypeScript (Vite, mounted only into specific DOM nodes, not a full SPA) + Zod (client-side UX validation only — DRF serializers are the real trust boundary) + DRF for the API + `django-vite` to inject built JS into templates.

Deploys to **Render** (this project ran on MySQL early on and was migrated to Postgres for Render compatibility — see git history around the migration commit if MySQL-era assumptions ever need double-checking). Production Postgres is hosted externally on **Neon** (free tier), not Render's own managed Postgres — Render has no free database tier, and provisioning any Render-managed DB forces a card on file for the whole Blueprint. Everything else (web service, static, media, email) still runs on Render; only `DATABASE_URL` points off-platform. `render.yaml`'s web service is on `plan: free`, which spins down after 15 minutes of inactivity — the first visitor after a spin-down waits ~30-60s for cold start.

To run locally, start both (React islands render blank without the Vite dev server):
```
venv\Scripts\python manage.py runserver 8000
cd frontend && npm run dev        # Vite on :5173
```
`npm run dev` spawns a detached `node` process that can survive a session end and keep :5173 occupied — check `netstat -ano | grep :5173` before assuming the port is free.

Tests:
```
pytest                            # backend, 162 tests (pytest-django)
cd frontend && npx vitest run     # frontend, 58 tests
cd e2e && npx playwright test     # e2e, needs both dev servers running — see e2e/README.md
```
No linter/formatter configured — match existing style.

## Architecture

- **`fireservice/`** is a thin project shell — settings only (`fireservice/settings/{base,dev,prod}.py`), root `urls.py` just includes `core.urls`.
- **`core`** owns every view and URL for the whole project. Domain apps (`leads`, `website`) own models/admin/serializers only — they have no views or urls of their own.
- One global `templates/` and one global `static/` (`css/`, `js/`, `image/`, `font/`, `files/`, `favicon/`, `SeedImages/`) at the repo root, plus `frontend/dist` (Vite build output) — all wired into `STATICFILES_DIRS`. `static/SeedImages/` holds source images no live template references directly: the originals for every DB-seeded `ClientLogo`/`Brand`/`Product`/`Certification`/`Service` row (migrations `0004`/`0006`/`0008`/`0012`/`0014` in `website/migrations/`), plus a handful of genuinely-orphaned leftovers. It's load-bearing, not dead weight — `media/` is gitignored, so these seed migrations are the *only* thing that repopulates real content on a fresh database (new clone, CI, deployment); don't delete files from here without checking whether a migration still reads them.
- **Public site** — 10 pages, each its own Django URL/template extending `templates/base.html`: Home, About, Services, Process, Clientele, Certifications, Contact, Survey, Consultation, Brochure.
- **`templates/includes/*.html`** — reusable partials (stats bars, contact info, logo, map embed, client-logo/brand/product grids, hero background slideshow, survey CTA banner, social icons). Check here before inlining repeated content. Any partial that reads a variable (e.g. `client_logos`, `brands`) must fetch it itself via a templatetag rather than relying on a sibling include to have set it — `{% include %}` gets its own context frame.
- **Admin Hub** — a custom client-facing CMS at `/admin-hub/` (session auth, single shared account, no per-user roles yet). Deliberately separate from Django's own `/admin/`, which stays mounted unused at its default location. Own base template (`templates/adminhub/base.html`, doesn't load `static/js/site.js` — that script hard-references public-page-only element IDs with no null checks) and its own off-canvas nav drawer (reuses the public site's `.nav` CSS verbatim below 1150px).
- **React islands** — `frontend/src/islands/<name>/{main.tsx, *.tsx, schema.ts}`, one Vite entry per island in `vite.config.ts`'s multi-entry `build.rollupOptions.input`. Shared code in `frontend/src/lib/`: `csrf.ts`, `api.ts` (DRF error parsing), `validators.ts` (shared Zod schemas incl. password-strength rules), `Modal.tsx` (portal-rendered into `document.body` — must be a portal, since a hovering ancestor with a CSS `transform` creates a containing block that traps a `position:fixed` descendant), `Skeleton.tsx` (shimmer loading state), and `useAddForm.ts`/`useCrudList.ts`/`useEditDelete.ts`/`useFormSubmit.ts` (shared CRUD hooks extracted across the admin islands). Islands: `survey-form`, `contact-form`, `consultation-form`, `admin-hub-login` (also hosts the Forgot Password flow), `admin-change-password` (renders as "Account Settings" — username/password/email management), `admin-site-settings`, `admin-mission-vision`, `admin-client-logos`, `admin-brands`, `admin-services`, `admin-fire-risk-items`, `admin-products`, `admin-process-phases`, `admin-certifications`.
- **Content models** (`website` app), each with an Admin Hub React island for CRUD, wired live into the matching public page: `MissionVisionItem`, `ClientLogo`, `Brand`, `Service`, `Product`, `FireRiskAssessmentItem` — all full Add/Edit/Delete via `Modal.tsx`. `Certification` is **Add/Delete only, no Edit** (deliberate — no PATCH/PUT route exists); supports uploading an image *or* a PDF (PDF's first page auto-rendered to an image via PyMuPDF on save). `SiteSetting` is a singleton (`pk=1` always, `.load()` helper) holding 5 numeric stats (years experience, clients served, installations, emergency support, team members), click-to-edit inline from the Admin Home header. `ProcessPhase` (name/image/order, managed from the Admin Hub Services page) backs the Process page's 7 phase photos — **wired positionally, not looped**: `ProcessView` passes the ordered queryset as `process_phases`, and `templates/process.html` looks each phase's photo up by list index (`process_phases.0` … `.6`) since the phase titles/taglines/explanation cards are still hardcoded copy, not DB-driven. Keeping exactly 7 rows in order is on the admin — deleting or reordering one shifts every phase's photo after it.
- **Leads** (`leads` app): `SurveyRequest`, `ContactMessage`, `ConsultationRequest` — reviewed via the Admin Hub Leads page (`/admin-hub/leads/`, tabbed one-table-at-a-time, paginated, resolvable) or Django's raw `/admin/` as a fallback. No email/SMS notification fires on new leads — a real SendGrid account exists (see Deployment below) but is only wired to OTP delivery, not lead-creation alerts.
- **Admin Home** (`/admin-hub/home/`) is a dark "command center" dashboard: today's-lead-count meters, a 30-day trend chart with a paginated daily-breakdown table below it, Recent Activity, and the `SiteSetting` stats row — separate dark theme scoped to this one page only, rest of Admin Hub stays on the light brand theme.
- **SEO**: `core/context_processors.py` (`seo`) emits canonical URLs, Open Graph/Twitter tags, and JSON-LD (`LocalBusiness`, `BreadcrumbList`, `Service`/`hasOfferCatalog` on Services). `templates/robots.txt` + `core/sitemaps.py` cover crawlability.

## Conventions & gotchas worth knowing before touching layout/infra

- `overflow-x:hidden` on both `html` and `body` (top of `style.css`) is **load-bearing** — the off-canvas mobile nav (`position:fixed` + `transform`) inflates `document.body.scrollWidth` in Chromium without it, letting mobile users scroll into empty space.
- That same `overflow-x:hidden` forces browsers to auto-compute `overflow-y:auto`, which silently breaks `position:sticky` for descendants — both the public and Admin Hub headers use `position:fixed` (with JS measuring real header height into `body`'s `padding-top`) instead of `sticky`.
- `django-vite` needs `'django_vite'` in `INSTALLED_APPS` in addition to the `DJANGO_VITE` settings dict, or `{% load django_vite %}` fails.
- PostgreSQL + `TIME_ZONE='Asia/Kolkata'`/`USE_TZ=True`: date-filtered queries (`created_at__date=...`) just work — Postgres ships its own IANA tz database, unlike the MySQL setup this project used briefly, which needed the `'UTC'`/`'Asia/Kolkata'` zone tables loaded manually (`mysql_tzinfo_to_sql.exe` was broken on that Windows install) and a service restart to clear a cached negative zone lookup. That whole class of "data is right but the query returns nothing" symptom doesn't apply here anymore.
- `manage.py dumpdata -o <file>` on Windows: the `-o` flag opens the output file with the console's locale codepage (cp1252), not UTF-8, so any non-ASCII character (e.g. an em dash) in the data corrupts the dump. Set `PYTHONUTF8=1` in the environment before running `dumpdata`/`loaddata` on Windows, or redirect stdout instead of using `-o`.
- The `fireservice_app` Postgres role needs `CREATEDB` — `pytest-django` creates/drops a `test_fireservice` database per run and fails with a permissions error otherwise (`ALTER ROLE fireservice_app CREATEDB;` as a superuser).
- A DRF `APIView.as_view()` is `csrf_exempt` by default, and `SessionAuthentication.enforce_csrf()` only runs once a user is already attached to the request — so any endpoint that must run **before** authentication (login, forgot-password OTP flows) is a plain Django `View` to keep real CSRF enforcement; once a request is already authenticated (change-password/username/email), an ordinary DRF `APIView` is safe.
- DRF's auto-inferred `ImageField` validates uploads by opening them with Pillow, which can't open SVG — any upload field that must accept SVG (e.g. service icons) needs an explicit `FileField` with its own content-type allowlist instead.
- CSS cascade: a longhand property override only wins if declared **after** any later shorthand rule of equal-or-lower specificity that also touches that property — declaring it earlier in the file loses silently regardless of how logically grouped the CSS looks.
- CSS Grid: a percentage `height` on a grid item whose row height is itself driven by a sibling column is an unreliable circular-size case — use `aspect-ratio` (self-determined) instead, and let siblings `flex:1` to match.
- Django's dev-server autoreloader can miss a newly-added function in an already-imported templatetags module, especially on Windows — restart `runserver` if a brand-new `{% tag %}` errors right after being added even though the code is correct.
- Browsers cache static JS/CSS across normal page loads (Django's dev server sends no cache-control headers) — a hard refresh rules out stale-cache before assuming new JS isn't being served.

## Content still needed from the client

- Real 14-person team group photo for the About page (currently a stand-in product photo).
- The Services and Process page intro photos have visible third-party branding baked in (an "IFS" logo, another company's "FIRE SERVICE ENGINEERING" text) — flagged, not fixed.
- Real testimonial quotes (none exist or have been fabricated).
- `achievements-growth-illustration.jpg` in the Home hero's photo slideshow is generic stock art that doesn't match the site's palette or the other 3 real photos in the rotation — cosmetic mismatch, not yet swapped.

## Known open issues / not yet built

- `media/certifications/` has ~190 orphaned duplicate files from past admin testing sessions (the file-cleanup signals work correctly for new uploads going forward; old orphans were never swept).
- The DB-driven image grids (`ClientLogo`/`Brand`/`Product` in `templates/includes/{client-logos,brands,products}.html`) don't set explicit `width`/`height` on their `<img>` tags, unlike the still-static images elsewhere — a minor CLS-prevention gap left by the `agent-seo` pass, which ran before these templates were fully DB-driven.
- Admin Hub login rate-limiting (5 failed attempts/5-minute window) uses Django's default per-process local-memory cache — not shared across multiple worker processes/machines in a real production deployment.
- Testimonials content management (no model/CRUD/island at all — the only originally-planned Admin Hub content type still missing).
- Per-user Admin Hub roles/permissions (still one shared login).
- Lead-creation email/SMS notifications (SMTP exists for OTP delivery only).

## Deployment (Render)

- **`render.yaml`** is the Blueprint — a single free-plan web service (`runtime: python`), deliberately no `databases:` block (see Neon note above — a Render-managed DB would force a card on file). Build step is `build.sh`: `pip install -r requirements/prod.txt`, then `npm ci && npm run build` inside `frontend/` (Render's native build image bundles `node`/`npm` alongside whichever runtime is selected, so this works without a Dockerfile), then `collectstatic`. Start command runs `migrate`, then `ensure_admin` (see below), then `gunicorn fireservice.wsgi:application`. `DATABASE_URL` is `sync: false` — filled in by hand with the Neon connection string, not Render-generated.
- **Admin Hub login bootstrap**: `core/management/commands/ensure_admin.py` creates the Admin Hub's one shared superuser account from `DJANGO_SUPERUSER_USERNAME`/`PASSWORD`/`EMAIL` env vars, idempotently (no-ops if that username already exists, no-ops if the env vars aren't set). Exists solely because **Render's free plan has no Shell/SSH access**, so `createsuperuser`'s interactive prompt can't be run against the deployed service — this runs unattended in `startCommand` on every restart instead. Content (client logos, brands, services, products, certifications, brochure, mission/vision, fire risk items, site settings, process phases, hero slides, blog posts) needs no equivalent bootstrap — all of it is already seeded by ordinary data migrations (`website/migrations/0002` through `0037`) and populates automatically the first time `migrate` runs against a fresh database.
- **Static files**: WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`, inserted right after `SecurityMiddleware` in `prod.py` only — dev keeps using `runserver`'s built-in static serving) with `CompressedManifestStaticFilesStorage`. Render's native web services have no separate static-file proxy/CDN, so without this `/static/` 404s in production even after `collectstatic` runs.
- **Media storage**: Cloudinary (`django-cloudinary-storage`), prod-only, configured in `prod.py` via `CLOUDINARY_CLOUD_NAME`/`CLOUDINARY_API_KEY`/`CLOUDINARY_API_SECRET` — fails closed (`ImproperlyConfigured`) if any are missing. This exists because Render's web-service disk is ephemeral and wipes on every deploy/restart; local dev is unaffected and keeps writing to `media/` on the filesystem as before. On the free Cloudinary tier initially — see `.env.example` for the account setup this needs before first deploy. Cloudinary's new-account default blocks public PDF/ZIP delivery (Settings → Security → "PDF and ZIP files delivery") — this project's Brochure/Certification PDFs need that switched on or reads 401.
- **Email (OTP delivery)**: migrated off Gmail SMTP to SendGrid via `django-anymail` (`anymail.backends.sendgrid.EmailBackend`, set in `base.py` so it's live in dev too) — `SENDGRID_API_KEY` and `DEFAULT_FROM_EMAIL` (must be a SendGrid-verified sender) required for OTP sends to actually work, but deliberately **not** fail-closed in `prod.py` (only a `RuntimeWarning` at boot) — the key is generated by hand at the client's office and shouldn't block a deploy that happens before it exists. Only the Admin Hub's "Forgot Password"/"Change Email" flows depend on it; nothing else does. Note: Anymail's SendGrid backend lost official upstream support in 2025 (Twilio pulled Anymail's shared test account) — it still works and Anymail has no plans to remove it, but it's no longer actively tested by the Anymail maintainers. The resulting `anymail.W003` warning is deliberately silenced via `SILENCED_SYSTEM_CHECKS` in both `base.py` and `prod.py`. `send_mail()` call sites in `core/api_views.py` were untouched — Anymail is a drop-in Django `EmailBackend`.
- **Logging**: `prod.py` defines an explicit `LOGGING` dict (console handler, root at INFO, `django.request` at ERROR) — without it, Django's built-in default only routes request errors to console when `DEBUG=True`, so a bare `DEBUG=False` deployment with no `ADMINS` configured would otherwise produce zero log output on a 500. Render captures stdout, so this is what actually shows up in the Render log stream.
- **CSRF**: `CSRF_TRUSTED_ORIGINS` is env-driven in `prod.py` (empty by default) — must be set to the deployed origin(s) (e.g. `https://iconic-techno-service.onrender.com`, plus any custom domain later) or POSTs from the React islands will 403.
- **`.env.example`** documents every env var the prod settings module reads. `render.yaml`'s `sync: false` entries are exactly the ones that need filling in by hand in the Render dashboard on first Blueprint sync (`SECRET_KEY` is `generateValue: true` instead — Render generates it).

## Custom agents

`.claude/agents/{agent-cleancode,agent-refactor,agent-security,agent-responsive}.md` — project-scoped FIND/FIX specialists (readability/reliability, cross-file duplication & dead code, security, mobile/responsive UX). FIND is read-only and reports findings; FIX only runs on an explicit follow-up command and never auto-triggers from a FIND report.

**SEO team (local-only, not in this list's git history):** `.claude/agents/agent-seo-*.md` — an
8-agent SEO team (`agent-seo-manager` orchestrating `agent-seo-strategist`,
`agent-seo-Technical-Architect`, `agent-seo-keyword`, `agent-seo-OP-optimization`,
`agent-seo-content-cluster-and-blog`, `agent-seo-SEO-GBP`, `agent-seo-link-building-outreach`) plus
its running activity log at `agent-seo-manager-memory.md` (repo root). Both the agent files and the
log are gitignored by request — deliberately local-only, not shared via this repo. If you're
reading this on a fresh clone, these files won't be present; ask whoever set them up for copies if
you need them.

## Current state

All work through commit `37b166e` is on `main`. 173 backend tests / 58 frontend tests passing; a Playwright e2e suite (`e2e/`, 6 spec files) runs against the real dev DB using a tagged-data cleanup convention (`core/management/commands/e2e_data.py`) — see `e2e/README.md` for scope and what isn't covered yet. Only one contact phone number remains sitewide (`+91 73592 29129`).

Migrated local dev + prod from MySQL to PostgreSQL (Render only offers Postgres as a managed DB). All real data (leads, admin user, content edits) was carried over via `dumpdata`/`loaddata`, not a fresh reseed — the MySQL server and its `fireservice` database were left untouched as a backup, not dropped.
