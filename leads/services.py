from datetime import timedelta

from django.utils import timezone

from .models import ConsultationRequest, ContactMessage, SurveyRequest

RESOLVED_LEAD_RETENTION_DAYS = 60

LEAD_MODELS = [SurveyRequest, ContactMessage, ConsultationRequest]


def purge_resolved_leads(retention_days=RESOLVED_LEAD_RETENTION_DAYS):
    """Deletes leads that were resolved more than `retention_days` ago.
    Called opportunistically from the Admin Hub Leads page (no background
    worker/cron exists in this stack — see CLAUDE.md's Render free-plan
    constraints) and also exposed as a management command for manual runs.
    Returns {model_name: deleted_count}.
    """
    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted_counts = {}
    for model in LEAD_MODELS:
        count, _ = model.objects.filter(resolved=True, resolved_at__lte=cutoff).delete()
        deleted_counts[model.__name__] = count
    return deleted_counts
