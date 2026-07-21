# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A single-page prototype website for a fire & life-safety systems company, built to show a client before real branding/content is finalized. Structurally and thematically inspired by the reference site `www.advancedfiresolutions.in` (an existing Ahmedabad-based fire safety provider), but redesigned rather than copied — improved visual design, added animation/interaction, restructured as a one-page scroll instead of separate PHP pages.

The company name used throughout ("FireGuard Solutions"), phone numbers, email, address, client logos, certificates, and testimonial are **all placeholders** and must be swapped for the real client's details before launch. Every image slot that needs a real photo/logo/certificate is a `.placeholder-img` block with a `data-placeholder="..."` attribute describing what should go there — grep for `placeholder-img` to find every one.

No backend exists yet. The contact form (`#contactForm`) only shows a UX message on submit ("connect it to email/CRM before launch") — it does not send data anywhere.

## Stack & commands

Plain static HTML/CSS/JS — no build step, no package manager, no bundler, no test suite.

To preview locally:
```bash
python -m http.server 8642
```
then open `http://localhost:8642`. Opening `index.html` directly via `file://` also works since there are no fetch calls or absolute paths.

There is no linter or formatter configured. Match existing style (double-space-free CSS shorthand, BEM-ish class names like `hero__content`, `card__icon`).

## Architecture

Everything lives in one page: `index.html` is a single scrolling document with anchor-linked sections (`#home`, `#about`, `#services`, `#process`, `#why`, `#clients`, `#certifications`, `#contact`), each a `<section class="section">`. The nav bar and footer both link to these anchors — there are no separate HTML pages.

**`css/style.css`** is organized top-down to match the page, prefixed by a design-tokens block (`:root` custom properties: `--red-*`, `--amber-500`, `--ink-*`, spacing/radius/shadow tokens). Reuse these variables rather than hardcoding colors. Responsive behavior is handled by three breakpoints (`1024px`, `860px`, `600px`) at the bottom of the file — the `860px` one is where the desktop nav becomes an off-canvas mobile drawer (`.nav` gets `position:fixed` + `transform: translateX(100%)`, toggled open via a `.open` class).

**Known CSS gotcha**: the off-canvas mobile nav (`position:fixed` + `transform`) inflates `document.body.scrollWidth` in Chromium even though it's visually off-screen, which would otherwise let mobile users scroll horizontally into empty space. `overflow-x:hidden` on both `html` and `body` (top of `style.css`) is load-bearing to prevent this — don't remove it when touching global layout rules.

**`js/script.js`** is one `DOMContentLoaded` listener with independent, unrelated concerns (not modularized since the file is small): footer year, mobile nav toggle, header scroll shadow, back-to-top button visibility, animated stat counters (`.stat__num[data-count]`, driven by `IntersectionObserver` + `requestAnimationFrame`), scroll-reveal fade-ins (`.reveal`/`.in` classes, also `IntersectionObserver`-driven), and the contact form's placeholder submit handler. When adding new sections with cards/steps that should fade in on scroll, add their selector to the `revealTargets` query rather than inventing a new observer.

## Content still needed from the client

Company name/logo/colors, real service list + photos, About copy, process steps (currently generic 4-step survey→design→install→handover), client logos/testimonials (with permission to display), certifications, team info, and final contact details. A full intake checklist for these was given to the user in conversation — ask them if it needs to be regenerated.

## Actual Development start

We will start the actual development in FireService!/ folder. FireService/ is a prototype version.

### Real build stack & scaffold plan

The prototype is being rebuilt on: **Django (server-rendered templates) + MySQL (SQLite for local dev, MySQL later via env var swap) + React "islands" in TypeScript + Zod for validation + Playwright for a minimal e2e suite + pytest-django/Vitest as the bulk of test coverage.** React is not a full SPA — it's mounted only into two isolated islands: the public contact form and the client-facing Admin Hub (custom-built, not Django's default `/admin/`) where the client manages Services, Certifications, Testimonials, and Client Logos.

The full original plan (data models, API surface, CSRF handling, testing strategy) was written during a planning session and saved to `C:\Users\shahb\.claude\plans\curried-greeting-wombat.md` on the user's machine. **Some structural decisions below have since evolved past what that file says** — this section is the up-to-date source of truth; treat the plan file as historical background, not current spec.

Key structural decisions locked in so far:
- Single shared venv at the repo root (`python -m venv venv`), `manage.py` at `FireService!/` root — no `backend/` wrapper folder.
- Django project package is named `fireservice`. It stays a thin project shell (settings + root `urls.py` that just does `include('core.urls')`) — it does **not** hold its own views.
- **`core` app owns all views and URLs for the project.** This supersedes the original plan's idea of each domain app (`website`, `leads`, `adminhub`) owning its own views/urls — domain apps will own models and business logic only; `core` is the one views/urls handler for every template. `core/views.py` currently has `HomeView`; `core/urls.py` currently has the `home` route (`/`), included from `fireservice/urls.py`.
- One **global** `templates/` folder at the repo root holds every template (currently `base.html`, `home.html` directly in `templates/`, not yet namespaced by app — revisit namespacing once more pages exist).
- One **global** `static/` folder at the repo root, with `css/`, `js/`, `image/`, `font/` subfolders, wired into `STATICFILES_DIRS` alongside `frontend/dist` (for the future Vite build output). This supersedes the original plan's per-app `website/static/website/...` layout.
- **The site is being restructured from one scrolling page into separate Django pages/URLs** — Home (`/`), About (`/about/`), Services (`/services/`), Process (`/process/`), Clientele (`/clientele/`), Certifications (`/certifications/`), Contact (`/contact/`). The prototype's "Why Choose Us" section has no nav link of its own, so it stays folded into the Home page (hero + stats + why-us) rather than getting its own page.
- Admin Hub login page is a plain Django template (session auth); only the authenticated dashboard is the React island.
- DRF for the API surface; `django-vite` to inject Vite-built React bundles into Django templates.

### Implementation status

Done so far (see git log on `main`, pushed to `https://github.com/shahbazkhan74659-crypto/FireService.git`):
- `venv/` created at repo root; `requirements/{base,dev,prod}.txt` written (`mysqlclient` kept in `prod.txt` only — deliberately not installed locally since dev runs SQLite and it's a Windows build-tooling risk otherwise). Dev deps installed: Django 5.2.16, djangorestframework, django-environ, Pillow, django-vite, pytest/pytest-django/pytest-cov/factory_boy.
- `fireservice` project scaffolded; settings split into `fireservice/settings/{base,dev,prod}.py` (`django-environ`-driven; `.env`, git-ignored, holds `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`/`DATABASE_URL`, currently `sqlite:///db.sqlite3`).
- `static/css/style.css` and `static/js/site.js` ported from the prototype — CSS verbatim (design tokens, breakpoints, the load-bearing `overflow-x:hidden` all intact); JS ported minus the contact-form submit handler (that logic moved into the contact-form React island instead, not `site.js`).
- `templates/base.html` — shared shell (topbar, header/nav, footer, back-to-top) with blocks `title`, `meta_description`, `extra_head`, `content`, `extra_scripts`. Nav/footer links are still hardcoded plain paths (`/about/`, `/services/`, etc.), **not** `{% url %}` yet, for the pages that don't exist yet — `/survey/` and `/contact/` are real routes now and already resolve correctly through those same hardcoded links.
- `templates/home.html` — extends `base.html`; Hero+stats and Why-Us sections. Hero background is a real photo (`static/image/bg-image.png`), not a placeholder. The hero's "Get Free Site Survey" CTA points at `/survey/`.
- `core` app: owns all views/urls for the whole project (locked decision, unchanged). Currently serves `HomeView` (`/`), `SurveyPageView` (`/survey/`), `ContactPageView` (`/contact/`) — the latter two both decorated with `ensure_csrf_cookie` since they host a React-island form with no server-rendered `{% csrf_token %}`. `core/api_views.py` holds the DRF `CreateAPIView`s for both forms (`SurveyRequestCreateView`, `ContactMessageCreateView`), both explicitly `permission_classes = [AllowAny]` to override the project-wide `IsAuthenticated` default in `REST_FRAMEWORK` settings.
- **`leads` app** (models/admin only, per the `core`-owns-views/urls split): `SurveyRequest` (name/email/address/problem/why_survey) and `ContactMessage` (name/phone/email/service-choice/message) models, both registered in Django admin — this is currently the only way leads are reviewed, since no email/SMTP is configured anywhere in the project (deliberately deferred, not an oversight).
- **Real client branding swapped in** (no longer placeholders): company name "Iconic Techno Service" (ITS) everywhere; real logo (`static/image/logo-its.png` light variant for dark backgrounds, `logo-its-dark.png` dark-text variant for light backgrounds — extracted/cropped/recolored from a client-provided PDF letterhead); real phone numbers for both contacts (Sanjay Barad, Keyur Padhiyar); real email, address, and GST number; real 8-item service list in the footer. Source assets referenced during this work lived outside the repo at `C:\FireService\ITS 01.pdf` and a WhatsApp-exported services image — already extracted into the site, not needed again unless the client sends updated branding.
- **`templates/includes/*.html`** — a small reusable-partial convention established for repeated content: `logo.html` (`light`/dark variant via a boolean flag), `address.html`, `email.html` (`icon` flag), `phone.html` (parametrized by `number`/`display`/`icon` — consolidated from two near-duplicate per-contact partials during a cleanup pass, see below), `services.html`, `map.html` (Google Maps `<iframe>` embed + "Open in Google Maps" link, no API key — built from a `cid=` embed URL resolved from the client's `maps.app.goo.gl` short link). When a new page needs any of this content, `{% include %}` the existing module rather than re-inlining it.
- **`frontend/` — real Vite + React + TypeScript workspace**, no longer just settings scaffolding: bootstrapped via `npm create vite@latest frontend -- --template react-ts`, SPA-only scaffold files removed (no `index.html`/`App.tsx` — Django serves the HTML, Vite only serves JS module assets). `vite.config.ts` is a **multi-entry** build (`build.rollupOptions.input`) with one entry per island; `base: '/static/'` is load-bearing and must equal Django's `STATIC_URL` (`django-vite`'s dev-server URL builder prepends `STATIC_URL` even in dev mode). Two islands exist so far, both under `frontend/src/islands/<name>/{main.tsx, <Name>Form.tsx, schema.ts}`: `survey-form` (mounts into `#survey-form-root` on `/survey/`) and `contact-form` (mounts into `#contact-form-root` on `/contact/`). Shared helpers live in `frontend/src/lib/`: `csrf.ts` (reads the `csrftoken` cookie — relies on `CSRF_COOKIE_HTTPONLY = False`, already set in `base.py` for exactly this), `api.ts` (`readErrorMessage()` — parses DRF's `{field: [msg, ...]}` error shape into a single display string), `validators.ts` (shared Zod `nameSchema`/`emailSchema` used by both islands' schemas). Both islands use the same `idle|submitting|success|error` state-machine shape and POST JSON with an `X-CSRFToken` header; server-side DRF serializers in `leads/serializers.py` independently re-validate everything (Zod is UX only, never the trust boundary).
  - **Gotcha, already hit once**: the Python `django-vite` package must *also* be added to `INSTALLED_APPS` (as `'django_vite'`) for its `{% load django_vite %}` templatetags to be discoverable — having `DJANGO_VITE` settings configured is not enough on its own.
  - **Gotcha, dev workflow**: `npm run dev` spawns a detached child `node` process; stopping the wrapping shell task (or a session restart) does not reliably kill it, so it can keep `localhost:5173` occupied invisibly. If a fresh `npm run dev` fails with `Port 5173 is already in use`, check `netstat -ano | grep :5173` for a stray `node.exe` and kill it directly before retrying.
- **Custom Claude Code agents** committed at `.claude/agents/{agent-cleancode,agent-refactor,agent-security}.md` (ported in from another project) — project-scoped FIND/FIX-mode specialist agents (readability/reliability, cross-file duplication & dead code, and security respectively). `.claude/settings.local.json` stays git-ignored (machine-specific), but the agent definitions themselves are checked in and available to any session working in this repo.
- Git repo pushed to `main` throughout; recent commits include real-content swaps, the Survey and Contact pages/islands ("Contact and Survay"), a refactor/cleanup pass ("Refactor and cleanup fixes" — deduplicated the DRF name validator, consolidated the two per-contact phone partials into one, extracted the shared frontend error-parsing and Zod helpers noted above), and the custom agents ("Added Agents").

Not started yet: the `website`/`adminhub` apps, the remaining pages (About/Services/Process/Clientele/Certifications), the Admin Hub React island (client-facing Services/Certifications/Testimonials/Client-logo management — distinct from the two public lead-capture islands that do exist now), Playwright/Vitest test setup (no test suite exists anywhere in the project yet, despite pytest-django being installed), and any email/SMTP notification on new leads (deliberately deferred — no credentials configured).