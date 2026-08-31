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

REPO_URL="https://github.com/shahbazkhan74659-crypto/FireService.git"
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
DB_PASSWORD="$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | cut -c1-24)"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
SQL

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

echo "==> Cloning the repo"
git clone "$REPO_URL" "$APP_DIR"
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
