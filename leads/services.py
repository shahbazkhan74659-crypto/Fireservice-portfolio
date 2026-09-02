import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import ConsultationRequest, ContactMessage, LeadNotificationCounter, SurveyRequest

logger = logging.getLogger(__name__)

RESOLVED_LEAD_RETENTION_DAYS = 60

LEAD_MODELS = [SurveyRequest, ContactMessage, ConsultationRequest]

LEAD_NOTIFICATION_COUNTER_FIELDS = {
    SurveyRequest: 'survey_count',
    ContactMessage: 'contact_count',
    ConsultationRequest: 'consultation_count',
}


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


def record_lead_created_and_maybe_notify(model, request=None):
    """Call once, right after a new lead row is saved, from each of the 3
    public CreateAPIViews' perform_create() (core/api_views.py). Atomically
    increments the shared cross-type LeadNotificationCounter; once the
    combined total reaches website.models.SiteSetting.load()'s configurable
    lead_notification_threshold, resets the counter to 0 and sends ONE
    bundled admin notification email summarizing the batch.

    transaction.atomic() + select_for_update() mirrors the TOCTOU-safe
    pattern core/api_views.py's perform_create overrides already use for
    order-increment (e.g. ClientLogoListCreateView) — closes the race where
    two concurrent lead submissions could both read total=24 and neither
    actually reach the threshold. The row lock is released before the email
    is sent, so a slow/hung SendGrid call never holds up other concurrent
    lead submissions waiting on the same counter row.

    Email delivery here is a side effect of an unrelated customer-facing
    action (submitting a public lead form) — unlike the OTP flows elsewhere
    in this project, a SendGrid outage must not break lead creation for the
    customer. The whole notification step is wrapped in try/except and only
    logged on failure, never re-raised; the counter reset itself already
    happened and isn't rolled back just because the email failed.
    """
    from website.models import SiteSetting  # local import: avoids a leads<->website import-order coupling

    LeadNotificationCounter.load()  # ensure the pk=1 row exists before locking it

    breakdown = None
    with transaction.atomic():
        counter = LeadNotificationCounter.objects.select_for_update().get(pk=1)
        field_name = LEAD_NOTIFICATION_COUNTER_FIELDS[model]
        setattr(counter, field_name, getattr(counter, field_name) + 1)

        threshold = SiteSetting.load().lead_notification_threshold
        if counter.total >= threshold:
            breakdown = {
                'total': counter.total,
                'survey': counter.survey_count,
                'contact': counter.contact_count,
                'consultation': counter.consultation_count,
            }
            counter.survey_count = 0
            counter.contact_count = 0
            counter.consultation_count = 0
        counter.save()

    if breakdown is not None:
        try:
            _send_lead_notification_email(breakdown, request)
        except Exception:
            logger.exception(
                'Failed to send bundled lead-notification email (total=%s)', breakdown['total'],
            )


def _send_lead_notification_email(breakdown, request):
    User = get_user_model()
    recipients = list(
        User.objects.filter(is_superuser=True, is_active=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )
    if not recipients:
        logger.warning(
            'Lead notification threshold hit (total=%s) but no active superuser has an '
            'email address set — skipping send.', breakdown['total'],
        )
        return

    leads_path = reverse('adminhub-leads')
    leads_url = request.build_absolute_uri(leads_path) if request is not None else leads_path

    subject = f"ICONIC TECHNO SERVICE — {breakdown['total']} New Leads"
    body = _lead_notification_email_body(breakdown, leads_url)
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)


def _lead_notification_email_body(breakdown, leads_url):
    return f"""Dear Administrator,

You have {breakdown['total']} new leads on ICONIC TECHNO SERVICE since the last notification.

---

Breakdown

Survey Requests: {breakdown['survey']}
Contact Messages: {breakdown['contact']}
Consultation Requests: {breakdown['consultation']}

---

Review and respond to these leads here:

{leads_url}

You will need to log in to the Admin Hub to view them.
"""
