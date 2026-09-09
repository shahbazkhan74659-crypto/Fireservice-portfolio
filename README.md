# Iconic Techno Service — Web Platform

Production website and lead-management platform for **Iconic Techno Service (ITS)**, a Silvassa-based fire & life-safety systems company. Live at **[iconictechnoservice.com](https://iconictechnoservice.com)**.

The public site markets ITS's services (fire alarm, gas suppression, hydrant systems, PAVA, safety equipment, and more) and captures leads (site surveys, contact, consultation requests). A companion **Admin Hub** lets the client manage content and review leads without touching code.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Database | PostgreSQL (via `django-environ` / `psycopg`) |
| Frontend | Server-rendered Django templates + React "islands" (TypeScript, Vite) mounted into specific pages |
| Validation | Zod (client-side UX only) + DRF serializers (real trust boundary) |
| Static/media build glue | `django-vite` |
| Hosting | Self-hosted Ubuntu VM on Oracle Cloud (nginx + gunicorn + systemd), HTTPS via Let's Encrypt/certbot |

## Project layout

```
core/            All views, URLs, API views, SEO/sitemap/context-processor logic
website/         Content models (Service, Product, ClientLogo, Testimonial, etc.), admin, serializers
leads/           Lead models (SurveyRequest, ContactMessage, ConsultationRequest) + notification logic
fireservice/     Project settings (base/dev/prod/oracle) and root URL config
templates/       Global Django templates (public site + Admin Hub)
static/          Global static assets (css, js, images, fonts, seed images)
frontend/        React islands (Vite + TypeScript), one entry per admin/public form widget
deploy/oracle/   Provisioning + deploy scripts for the production VM
e2e/             Playwright end-to-end tests
```

See [`CLAUDE.md`](./CLAUDE.md) for the full architectural deep-dive (content models, Admin Hub design, deployment history, known issues) — it's the living source of truth for how this project actually works.

## Getting started (local dev)

**Prerequisites:** Python 3.10+, Node.js, PostgreSQL (local instance with a role that has `CREATEDB`).

1. **Clone and configure environment**
   ```bash
   git clone git@github.com:<your-org>/FireService.git
   cd FireService
   cp .env.example .env   # fill in DATABASE_URL, SECRET_KEY, etc.
   ```

2. **Backend**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install -r requirements/dev.txt
   python manage.py migrate
   python manage.py runserver 8000
   ```

3. **Frontend** (React islands render blank without this running)
   ```bash
   cd frontend
   npm install
   npm run dev                    # Vite dev server on :5173
   ```

4. Visit `http://localhost:8000`. Admin Hub is at `/admin-hub/`.

## Running tests

```bash
pytest                          # backend (pytest-django)
cd frontend && npx vitest run   # frontend
cd e2e && npx playwright test   # end-to-end (needs both dev servers running — see e2e/README.md)
```

## Deployment

Production runs on a self-hosted Oracle Cloud VM (no CI/auto-deploy). Deployment steps, provisioning scripts, and environment setup live in [`deploy/oracle/README.md`](./deploy/oracle/README.md).

## License

Proprietary — all rights reserved. This codebase is built for and owned by Iconic Techno Service; it is not licensed for reuse or redistribution.
