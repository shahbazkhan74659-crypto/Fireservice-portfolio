import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Idempotently creates the Admin Hub's one shared login account from
    DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD env vars. Exists because
    Render's free plan has no Shell/SSH access, so `createsuperuser`'s
    interactive prompt can't be run against the deployed service — this
    runs unattended in the start command instead, safe to run on every
    restart since it never touches an account that already exists.
    """
    help = 'Create the Admin Hub superuser from env vars if it does not already exist.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME/PASSWORD not set — skipping.')
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Superuser "{username}" already exists — left unchanged.')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}".'))
