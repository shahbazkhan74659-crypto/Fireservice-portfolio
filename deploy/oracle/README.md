# Oracle VM deploy scripts

Scaffolding for the parallel Oracle Cloud deployment described in CLAUDE.md's "Planned:
possible migration off Render to Oracle Cloud" section. Render (on Neon) stays live and
authoritative until this is proven stable — nothing here touches Render.

## Order of operations

1. **Console steps first** (CLAUDE.md's Oracle migration section): create the VM
   (`VM.Standard.E2.1.Micro`, Ubuntu 24.04, reserved public IP, security list rules for
   80/443), create the `its-db-backups` Object Storage bucket, and add an API key to the
   `deploy-admins` IAM user for backup uploads.
2. `scp` two sets of secrets to the VM (not scripted — provision.sh checks for them and
   errors with instructions if either is missing):
   - The Oracle API key from step 1: `~/.oci/config` and whatever key path it references.
   - A GitHub deploy key's **private** half, to `~/.ssh/github_deploy_key` (mode `600`).
     `FireService` is a private repo, so `provision.sh` clones over SSH using this key —
     generate a dedicated keypair (`ssh-keygen -t ed25519 -f deploy_key -N ""`), register
     the **public** half as a read-only deploy key on the repo (Settings → Deploy keys, or
     `gh repo deploy-key add deploy_key.pub --title "<vm-name>" --repo
     shahbazkhan74659-crypto/FireService`), then scp the private half over.
3. SSH in with `~/.ssh/oracle_its_vm` and run `provision.sh` (this repo's copy, or `curl`
   it — either way, read it before running it, standard practice for any setup script).
   It installs everything, creates the Postgres role/DB, clones the repo, and seeds `.env`
   from `.env.oracle.example` — then stops and prints the generated DB password plus the
   remaining manual steps (below). Safe to re-run if it fails partway through (e.g. a
   missing secret from step 2) — the apt/swapfile/Postgres/clone steps are all idempotent.
4. Fill in the real secrets in `~/FireService/.env` (SECRET_KEY, ALLOWED_HOSTS,
   CSRF_TRUSTED_ORIGINS, DJANGO_SUPERUSER_*, SENDGRID_API_KEY).
5. Run `deploy.sh` — builds the frontend, runs migrations/`ensure_admin`, and (once the
   systemd unit exists, next step) restarts the app.
6. Install the systemd unit:
   ```
   sudo cp deploy/oracle/gunicorn-its.service /etc/systemd/system/gunicorn-its.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now gunicorn-its
   ```
7. Install the nginx site:
   ```
   sudo cp deploy/oracle/nginx.conf /etc/nginx/sites-available/its
   sudo ln -s /etc/nginx/sites-available/its /etc/nginx/sites-enabled/its
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```
8. Install the nightly backup cron job:
   ```
   sudo cp deploy/oracle/its-db-backup.cron /etc/cron.d/its-db-backup
   sudo chmod 644 /etc/cron.d/its-db-backup
   ```
   Trigger it once by hand (`./backup-db.sh`) and confirm the object actually lands in
   the bucket before trusting the schedule.
9. From your own machine: `curl http://<reserved-public-ip>/` to confirm the homepage
   renders, and spot-check a `/static/...` and `/media/...` URL.

## Redeploying later

Just `deploy.sh` — it's `git pull` + rebuild + migrate + restart, nothing else needed.

## What's deliberately not here yet

- HTTPS/certbot — the domain (`iconictechnoservice.com`) is purchased, but DNS hasn't
  been pointed at this VM yet (gated on the reserved public IP step above), so certbot
  hasn't been run.
- Migrating real production data (Neon → this VM's Postgres) or real media
  (Cloudinary → this VM's disk) — this stack starts from a fresh, migration-seeded
  database until the deployment is confirmed stable and an actual cutover is decided on.
