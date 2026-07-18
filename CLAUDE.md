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

Key structural decisions locked in for this build:
- Single shared venv at the repo root (`python -m venv venv`), `manage.py` at `FireService!/` root — no `backend/` wrapper folder.
- Django project package is named `fireservice` (not the generic `config`).
- One **global** `templates/` folder at the repo root holds every template, namespaced by app subfolder (`templates/website/...`, `templates/adminhub/...`) — not per-app `templates/` dirs.
- Apps: `website` (public content/models), `leads` (contact submissions), `adminhub` (auth + DRF CRUD API, reuses `website`/`leads` models rather than owning its own).
- Admin Hub login page is a plain Django template (session auth); only the authenticated dashboard is the React island.
- DRF for the API surface; `django-vite` to inject Vite-built React bundles into Django templates.

The full detailed plan (repo layout, data models, API surface, CSRF handling, testing strategy, and step-by-step build sequencing) was written during a planning session and saved to `C:\Users\shahb\.claude\plans\curried-greeting-wombat.md` on the user's machine — read that file for the complete scaffold plan before starting or resuming this build.