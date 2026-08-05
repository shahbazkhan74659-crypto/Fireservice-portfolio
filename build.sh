#!/usr/bin/env bash
# Render build step: installs both toolchains, builds the Vite bundle, then
# collects everything (Django static + the Vite build output already wired
# into STATICFILES_DIRS) into STATIC_ROOT for WhiteNoise to serve.
set -o errexit

pip install -r requirements/prod.txt

cd frontend
npm ci
npm run build
cd ..

python manage.py collectstatic --noinput
