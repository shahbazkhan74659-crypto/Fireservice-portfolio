# CLAUDE.md

Guidance for Claude Code when working in this repo.

## Project

Real production build for **Iconic Techno Service (ITS)**, a Silvassa-based fire & life-safety systems company. Real branding is live throughout (name, logo, phones, address, GST, service list) — nothing here is placeholder content anymore.

A static single-page prototype exists at the sibling folder `C:\FireService\` (no `!`) — historical reference only, fully superseded by this build. An original planning doc also exists at `C:\Users\shahb\.claude\plans\curried-greeting-wombat.md`; treat it as historical background too — this file is the up-to-date source of truth.

**Don't use the Chrome browser automation extension unless explicitly told to.**

## Stack & commands

Django 5.2 (server-rendered templates) + MySQL (local dev, via `django-environ`/`.env`) + React "islands" in TypeScript (Vite, mounted only into specific DOM nodes, not a full SPA) + Zod (client-side UX validation only — DRF serializers are the real trust boundary) + DRF for the API + `django-vite` to inject built JS into templates.

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
- **Leads** (`leads` app): `SurveyRequest`, `ContactMessage`, `ConsultationRequest` — reviewed via the Admin Hub Leads page (`/admin-hub/leads/`, tabbed one-table-at-a-time, paginated, resolvable) or Django's raw `/admin/` as a fallback. No email/SMS notification fires on new leads — real SMTP credentials exist (see below) but are only wired to OTP delivery, not lead-creation alerts.
- **Admin Home** (`/admin-hub/home/`) is a dark "command center" dashboard: today's-lead-count meters, a 30-day trend chart with a paginated daily-breakdown table below it, Recent Activity, and the `SiteSetting` stats row — separate dark theme scoped to this one page only, rest of Admin Hub stays on the light brand theme.
- **SEO**: `core/context_processors.py` (`seo`) emits canonical URLs, Open Graph/Twitter tags, and JSON-LD (`LocalBusiness`, `BreadcrumbList`, `Service`/`hasOfferCatalog` on Services). `templates/robots.txt` + `core/sitemaps.py` cover crawlability.

## Conventions & gotchas worth knowing before touching layout/infra

- `overflow-x:hidden` on both `html` and `body` (top of `style.css`) is **load-bearing** — the off-canvas mobile nav (`position:fixed` + `transform`) inflates `document.body.scrollWidth` in Chromium without it, letting mobile users scroll into empty space.
- That same `overflow-x:hidden` forces browsers to auto-compute `overflow-y:auto`, which silently breaks `position:sticky` for descendants — both the public and Admin Hub headers use `position:fixed` (with JS measuring real header height into `body`'s `padding-top`) instead of `sticky`.
- `django-vite` needs `'django_vite'` in `INSTALLED_APPS` in addition to the `DJANGO_VITE` settings dict, or `{% load django_vite %}` fails.
- MySQL + `TIME_ZONE='Asia/Kolkata'`/`USE_TZ=True`: date-filtered queries (`created_at__date=...`) generate `CONVERT_TZ(col, 'UTC', 'Asia/Kolkata')`, which silently returns `NULL` unless **both** the `'UTC'` and `'Asia/Kolkata'` named zones are loaded into `mysql.time_zone*`. `mysql_tzinfo_to_sql.exe` is broken on this Windows install regardless of input — the zones were inserted manually. MySQL also caches a negative zone lookup per-process, surviving `FLUSH TABLES` — a real service restart was needed after fixing the data. Watch for this class of "the data is right but the query still returns nothing" symptom.
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

## Custom agents

`.claude/agents/{agent-cleancode,agent-refactor,agent-security,agent-responsive,agent-seo}.md` — project-scoped FIND/FIX specialists (readability/reliability, cross-file duplication & dead code, security, mobile/responsive UX, technical SEO). FIND is read-only and reports findings; FIX only runs on an explicit follow-up command and never auto-triggers from a FIND report.

## Current state

All work through commit `94c2410` is on `main`, working tree clean. 162 backend tests / 58 frontend tests passing; a Playwright e2e suite (`e2e/`, 6 spec files) runs against the real dev DB using a tagged-data cleanup convention (`core/management/commands/e2e_data.py`) — see `e2e/README.md` for scope and what isn't covered yet. Only one contact phone number remains sitewide (`+91 73592 29129`).
