from django.core.management.base import BaseCommand

from leads.services import purge_resolved_leads


class Command(BaseCommand):
    """Manual/standalone entry point for the same cleanup that runs
    opportunistically on every Admin Hub Leads page load (AdminHubLeadsView)
    — useful for a one-off run without visiting the site.
    """
    help = 'Delete resolved leads (survey/contact/consultation) whose resolved_at is more than 60 days old.'

    def handle(self, *args, **options):
        deleted_counts = purge_resolved_leads()
        total = sum(deleted_counts.values())
        if total == 0:
            self.stdout.write('No resolved leads older than the retention window — nothing deleted.')
            return
        for model_name, count in deleted_counts.items():
            if count:
                self.stdout.write(f'Deleted {count} resolved {model_name}(s).')
        self.stdout.write(self.style.SUCCESS(f'Deleted {total} lead(s) total.'))
