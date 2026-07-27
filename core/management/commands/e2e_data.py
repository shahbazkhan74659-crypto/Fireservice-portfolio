from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from website.models import Brand

# Fixed, well-known credentials for the Playwright suite's global setup/
# teardown (e2e/global-setup.ts, e2e/global-teardown.ts) — not a secret,
# this account only ever exists transiently against a local dev server.
E2E_USERNAME = 'e2e_admin'
E2E_PASSWORD = 'E2eTestAdmin123!'

# Every lead/content row created by the suite uses this as its name/prefix
# so teardown can find and remove exactly (and only) what the suite made,
# without touching real data sitting in the same dev database.
E2E_MARKER = 'E2E Test Runner'


class Command(BaseCommand):
    help = (
        'Create or remove the throwaway admin account and marker-tagged '
        'lead/content rows used by the Playwright e2e suite (e2e/). Run '
        'against the same dev database the suite\'s target server uses — '
        'this is not a separate test database.'
    )

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['setup', 'teardown'])

    def handle(self, *args, **options):
        if options['action'] == 'setup':
            self._setup()
        else:
            self._teardown()

    def _setup(self):
        User.objects.filter(username=E2E_USERNAME).delete()
        User.objects.create_superuser(E2E_USERNAME, 'e2e@example.com', E2E_PASSWORD)
        self.stdout.write(self.style.SUCCESS(f'e2e_data: created {E2E_USERNAME}'))

    def _teardown(self):
        User.objects.filter(username=E2E_USERNAME).delete()
        deleted = 0
        for model in (SurveyRequest, ContactMessage, ConsultationRequest):
            n, _ = model.objects.filter(name=E2E_MARKER).delete()
            deleted += n
        n, _ = Brand.objects.filter(name__startswith=E2E_MARKER).delete()
        deleted += n
        self.stdout.write(self.style.SUCCESS(
            f'e2e_data: removed {E2E_USERNAME} and {deleted} marker-tagged row(s)'
        ))
