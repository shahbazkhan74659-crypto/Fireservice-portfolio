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
- `static/css/style.css` and `static/js/site.js` ported from the prototype — CSS verbatim (design tokens, breakpoints, the load-bearing `overflow-x:hidden` all intact); JS ported minus the contact-form submit handler (that logic moves to the future contact-form React island, not into `site.js`).
- `templates/base.html` — shared shell (topbar, header/nav, footer, back-to-top) with blocks `title`, `meta_description`, `extra_head`, `content`, `extra_scripts`. Nav/footer links currently hardcoded plain paths (`/about/`, `/services/`, etc.), **not** `{% url %}` yet — swap these once each page's URL is actually registered.
- `templates/home.html` — extends `base.html`; contains Hero+stats and Why-Us sections ported from the prototype's markup/classes.
- `core` app created, registered in `INSTALLED_APPS`, serving `/` via `HomeView` → `home.html`.
- Git repo initialized in `FireService!/`, remote `origin` added, two commits pushed to `main`: "Project Planning" and "Initial development and Home page".

Not started yet: the `website`/`leads`/`adminhub` apps and their models, the remaining pages (About/Services/Process/Clientele/Certifications/Contact), the contact-form and Admin Hub React islands, the `frontend/` Vite+TS workspace, Zod schemas, Playwright/Vitest test setup.