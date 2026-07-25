from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

DEBUG = False

# base.py falls back to a known, publicly-visible insecure SECRET_KEY when
# SECRET_KEY isn't set in .env, so local dev never hard-fails on a missing
# env file. That fallback must never reach production — fail closed instead
# of silently booting with a key an attacker could look up in this repo.
if not SECRET_KEY or SECRET_KEY == 'django-insecure-change-me-in-.env':
    raise ImproperlyConfigured(
        'SECRET_KEY is missing or still set to the insecure development '
        'default. Set a real, unique SECRET_KEY in the production .env '
        'before starting this server.'
    )

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Standard hardening for a deployment behind a TLS-terminating reverse proxy.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

DJANGO_VITE = {
    'default': {
        'dev_mode': False,
        'manifest_path': BASE_DIR / 'frontend' / 'dist' / '.vite' / 'manifest.json',
    }
}
