#!/usr/bin/env bash
# One-time bootstrap for a fresh Oracle Cloud VM (Ubuntu 24.04,
# VM.Standard.E2.1.Micro). Run this over SSH as the `ubuntu` user, once,
# right after the instance is created — see CLAUDE.md's Oracle migration
# section for the Console steps that come before this (VM creation, the
# Object Storage bucket, and the deploy-admins API key).
#
# After this script finishes, fill in the real secrets in ~/FireService/.env
# (it only copies the .env.oracle.example template — see that file's
# comments) and the Postgres password it prints below, then run deploy.sh.
set -euo pipefail

# FireService is a private repo — cloning over plain HTTPS fails non-interactively
# ("could not read Username for 'https://github.com'"). Use a read-only GitHub
# deploy key instead: generate one, register its public half at
# https://github.com/shahbazkhan74659-crypto/FireService/settings/keys (or via
# `gh repo deploy-key add`), then scp the PRIVATE half to this VM at
# ~/.ssh/github_deploy_key before running this script (chmod 600 it).
REPO_URL="git@github.com:shahbazkhan74659-crypto/FireService.git"
APP_DIR="$HOME/FireService"
DB_NAME="fireservice"
DB_USER="fireservice_app"

echo "==> apt update/upgrade"
sudo apt-get update
sudo apt-get upgrade -y

echo "==> Installing base packages"
sudo apt-get install -y \
    python3-venv python3-pip \
    nginx git ufw unattended-upgrades \
    certbot python3-certbot-nginx \
    postgresql postgresql-contrib \
    pipx

echo "==> Installing Node.js 22.x (NodeSource) — needed for 'npm run build'"
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "==> Installing oci-cli (for nightly DB backups to Object Storage)"
pipx ensurepath
pipx install oci-cli
echo "    NOTE: still need to scp the API key downloaded from the Console"
echo "    to ~/.oci/config + its key file — provision.sh does not do this,"
echo "    it's a secret. See CLAUDE.md's Oracle migration section."

# 1GB RAM is tight for a running Postgres instance *and* a Vite/tsc build
# at the same time during deploys — a swapfile absorbs that peak instead
# of risking the OOM killer. Idempotent: skip if one already exists.
if [ ! -f /swapfile ]; then
    echo "==> Creating 4GB swapfile"
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
else
    echo "==> Swapfile already exists, skipping"
fi

echo "==> Enabling unattended security upgrades"
sudo dpkg-reconfigure -f noninteractive unattended-upgrades

echo "==> Configuring firewall (ufw)"
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "==> Creating Postgres role + database"
# Idempotent: safe to re-run this script if an earlier step failed partway
# through (e.g. the git clone below) without needing to hand-fix Postgres first.
DB_PASSWORD="$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | cut -c1-24)"
# NOTE: psql's `:'var'` substitution does not apply inside a $$-quoted PL/pgSQL
# body (psql's lexer treats it as one opaque token), so bash-level substitution
# is used instead — safe here since DB_USER is a fixed literal and DB_PASSWORD
# is alphanumeric-only (no quotes/specials to worry about).
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
   ELSE
      ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$\$;
SQL
sudo -u postgres psql -v ON_ERROR_STOP=1 -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || \
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

# Tune down defaults for the 1GB-RAM shape. Debian/Ubuntu's postgresql.conf
# includes conf.d/*.conf by default — drop a small override file instead of
# editing the shipped conf directly.
PG_VERSION="$(psql -V | grep -oE '[0-9]+' | head -1)"
PG_CONF_D="/etc/postgresql/${PG_VERSION}/main/conf.d"
sudo mkdir -p "$PG_CONF_D"
sudo tee "${PG_CONF_D}/oracle-vm-tuning.conf" > /dev/null <<'CONF'
shared_buffers = 128MB
work_mem = 8MB
maintenance_work_mem = 32MB
CONF
sudo systemctl restart postgresql

echo "==> Configuring SSH for the GitHub deploy key"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
if [ ! -f ~/.ssh/github_deploy_key ]; then
    echo "ERROR: ~/.ssh/github_deploy_key not found." >&2
    echo "scp the deploy key's PRIVATE half here first (see REPO_URL comment above), then re-run." >&2
    exit 1
fi
chmod 600 ~/.ssh/github_deploy_key
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null
grep -q "^Host github.com" ~/.ssh/config 2>/dev/null || cat >> ~/.ssh/config <<'SSHCONF'
Host github.com
    IdentityFile ~/.ssh/github_deploy_key
    IdentitiesOnly yes
SSHCONF
chmod 600 ~/.ssh/config

echo "==> Cloning the repo"
if [ -d "$APP_DIR/.git" ]; then
    echo "    $APP_DIR already exists, skipping clone"
else
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

echo "==> Creating venv and installing Python dependencies"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements/oracle.txt

echo "==> Seeding .env from template"
cp .env.oracle.example .env
sed -i "s#^DATABASE_URL=.*#DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}#" .env

cat <<EOF

============================================================
Provisioning done. Before running deploy.sh:

1. Copy the Oracle API key files (from the Console step in
   CLAUDE.md) to ~/.oci/config and its referenced key path.

2. Edit ${APP_DIR}/.env and fill in:
     SECRET_KEY          (generate one, e.g. via Django's get_random_secret_key)
     ALLOWED_HOSTS        (this VM's reserved public IP)
     CSRF_TRUSTED_ORIGINS (http://<reserved-public-ip>)
     DJANGO_SUPERUSER_*   (Admin Hub login)
     SENDGRID_API_KEY / DEFAULT_FROM_EMAIL (can reuse Render's)
   DATABASE_URL is already filled in below — the generated Postgres
   password for role "${DB_USER}" is:

       ${DB_PASSWORD}

   (also save this somewhere safe — it is not stored anywhere else)

3. Run deploy/oracle/deploy.sh to build the frontend, migrate, and
   start the app for the first time.

4. Copy deploy/oracle/gunicorn.service to
   /etc/systemd/system/gunicorn-its.service, then:
       sudo systemctl daemon-reload
       sudo systemctl enable --now gunicorn-its

5. Copy deploy/oracle/nginx.conf to
   /etc/nginx/sites-available/its, symlink it into sites-enabled,
   remove the default site, then: sudo nginx -t && sudo systemctl reload nginx

6. Copy deploy/oracle/backup-db.sh's companion cron.d file into
   /etc/cron.d/ (see deploy/oracle/README.md) for nightly backups.
============================================================
EOF
