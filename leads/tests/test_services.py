from datetime import timedelta

import pytest
from django.utils import timezone

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.services import purge_resolved_leads

pytestmark = pytest.mark.django_db


class TestPurgeResolvedLeads:
    def test_deletes_only_resolved_leads_past_the_retention_window(self):
        stale = SurveyRequest.objects.create(
            name='Stale', email='stale@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
            resolved=True, resolved_at=timezone.now() - timedelta(days=61),
        )
        recent = SurveyRequest.objects.create(
            name='Recent', email='recent@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
            resolved=True, resolved_at=timezone.now() - timedelta(days=1),
        )
        unresolved = SurveyRequest.objects.create(
            name='Unresolved', email='open@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )

        deleted_counts = purge_resolved_leads()

        assert deleted_counts['SurveyRequest'] == 1
        assert not SurveyRequest.objects.filter(pk=stale.pk).exists()
        assert SurveyRequest.objects.filter(pk=recent.pk).exists()
        assert SurveyRequest.objects.filter(pk=unresolved.pk).exists()

    def test_covers_all_three_lead_types(self):
        now = timezone.now()
        stale_cutoff = now - timedelta(days=61)
        ContactMessage.objects.create(
            name='Stale Contact', phone='9876543210', email='stale@example.com',
            resolved=True, resolved_at=stale_cutoff,
        )
        ConsultationRequest.objects.create(
            name='Stale Consultation', phone='9876543210',
            resolved=True, resolved_at=stale_cutoff,
        )

        deleted_counts = purge_resolved_leads()

        assert deleted_counts == {'SurveyRequest': 0, 'ContactMessage': 1, 'ConsultationRequest': 1}
        assert ContactMessage.objects.count() == 0
        assert ConsultationRequest.objects.count() == 0

    def test_custom_retention_window(self):
        SurveyRequest.objects.create(
            name='Ten Days Ago', email='x@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
            resolved=True, resolved_at=timezone.now() - timedelta(days=10),
        )

        deleted_counts = purge_resolved_leads(retention_days=5)

        assert deleted_counts['SurveyRequest'] == 1
        assert SurveyRequest.objects.count() == 0
