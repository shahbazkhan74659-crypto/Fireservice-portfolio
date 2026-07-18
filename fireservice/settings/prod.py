from .base import *  # noqa: F401,F403

DEBUG = False

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DJANGO_VITE = {
    'default': {
        'dev_mode': False,
        'manifest_path': BASE_DIR / 'frontend' / 'dist' / '.vite' / 'manifest.json',
    }
}
