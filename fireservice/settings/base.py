"""
Base Django settings for the fireservice project, shared by dev.py and prod.py.
"""

from pathlib import Path

import environ

# BASE_DIR resolves to the repo root (FireService!/), since manage.py lives there.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-.env')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'rest_framework',
    'django_vite',
    'anymail',

    'core',
    'leads',
    'website',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.EnsureCsrfCookieMiddleware',
]

ROOT_URLCONF = 'fireservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Global templates folder — every project-authored template lives here,
        # namespaced by app subfolder (templates/website/..., templates/adminhub/...).
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.seo',
            ],
        },
    },
]

WSGI_APPLICATION = 'fireservice.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# SQLite fallback for a bare clone; real dev/prod both run on PostgreSQL via
# DATABASE_URL — swap is DATABASE_URL only, no code change.

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'core.password_validators.UppercaseValidator'},
    {'NAME': 'core.password_validators.SpecialCharacterValidator'},
    {'NAME': 'core.password_validators.NoWhitespaceValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# Backs core/rate_limit.py's login-lockout counters (and AdminHubLoginAPIView's
# own inline copy). Postgres-backed rather than the default local-memory
# cache so lockouts are actually shared across gunicorn's worker processes —
# a local-memory cache would let an attacker get N attempts per worker
# instead of N total. No new service to run (unlike Redis/memcached) since
# every environment (dev/prod/oracle) already has Postgres; the table itself
# is created by core's 0001 migration via `createcachetable`.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}


# Static & media files

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'frontend' / 'dist',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/min',
    },
}

# CSRF cookie must stay JS-readable (Django default) so React islands can
# read it and set X-CSRFToken on POST/PUT/PATCH/DELETE fetch calls.
CSRF_COOKIE_HTTPONLY = False

LOGIN_URL = '/admin-hub/'
LOGIN_REDIRECT_URL = '/admin-hub/home/'


# Email — used for the Admin Hub "Forgot Password" and "Change Email" OTP
# flows. Sent via SendGrid (through django-anymail) rather than raw SMTP.
# `send_mail()` call sites in core/api_views.py are unchanged — Anymail is a
# drop-in Django EmailBackend, so only this config swap was needed.
# DEFAULT_FROM_EMAIL must be an address verified in SendGrid (Single Sender
# Verification or domain authentication) or sends will be rejected.
EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='iconictechnoservice.in@gmail.com')

ANYMAIL = {
    'SENDGRID_API_KEY': env('SENDGRID_API_KEY', default=''),
}

# Anymail's SendGrid backend lost official upstream support in 2025 (Twilio
# revoked Anymail's test account) but still works and has no removal planned
# — accepted knowingly, see anymail.W003. Silenced so deploy logs stay clean.
SILENCED_SYSTEM_CHECKS = ['anymail.W003']
