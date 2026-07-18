from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Vite dev server integration toggles with DEBUG — see frontend/ setup (later step).
DJANGO_VITE = {
    'default': {
        'dev_mode': DEBUG,
        'dev_server_port': 5173,
        'manifest_path': BASE_DIR / 'frontend' / 'dist' / '.vite' / 'manifest.json',
    }
}
