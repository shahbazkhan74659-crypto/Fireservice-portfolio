#!/usr/bin/env bash
# Repeatable redeploy — run this on the VM (over SSH) every time there's a
# new commit to ship. Mirrors what build.sh does for Render's build step,
# plus the migrate/restart that Render's startCommand normally handles.
set -euo pipefail

export DJANGO_SETTINGS_MODULE=fireservice.settings.oracle

cd "$(dirname "$0")/../.."

git pull

source venv/bin/activate
pip install -r requirements/oracle.txt

cd frontend
npm ci
npm run build
cd ..

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py ensure_admin

sudo systemctl restart gunicorn-its
echo "==> Deployed. sudo systemctl status gunicorn-its to confirm it's running."
