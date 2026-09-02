import pytest
from django.core import mail
from django.urls import reverse

from leads.models import ConsultationRequest, ContactMessage, LeadNotificationCounter, SurveyRequest
from website.models import SiteSetting

pytestmark = pytest.mark.django_db

SURVEY_PAYLOAD = {
    'name': 'Jane Doe', 'email': 'jane@example.com',
    'address': '123 Long Enough Street Address, City',
    'problem': 'The fire alarm panel keeps beeping intermittently at night.',
    'why_survey': 'We need an on-site assessment before renewing our AMC contract.',
}
CONTACT_PAYLOAD = {'name': 'Jane Doe', 'phone': '9876543210', 'email': 'jane@example.com', 'service': 'fire_detection'}
CONSULTATION_PAYLOAD = {'name': 'Jane Doe', 'phone': '9876543210'}


@pytest.fixture(autouse=True)
def _clear_outbox():
    mail.outbox.clear()
    yield


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_superuser('admin', 'admin@example.com', 'pw12345!')


@pytest.fixture
def low_threshold():
    setting = SiteSetting.load()
    setting.lead_notification_threshold = 3
    setting.save()
    return setting


class TestBundledLeadNotification:
    def test_no_email_below_threshold(self, client, superuser, low_threshold):
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        client.post(reverse('api-contact'), CONTACT_PAYLOAD)

        assert len(mail.outbox) == 0
        assert LeadNotificationCounter.load().total == 2

    def test_email_sent_exactly_at_threshold_with_combined_total_across_types(self, client, superuser, low_threshold):
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        client.post(reverse('api-contact'), CONTACT_PAYLOAD)
        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)

        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.to == ['admin@example.com']
        assert '3 New Leads' in message.subject
        assert 'Survey Requests: 1' in message.body
        assert 'Contact Messages: 1' in message.body
        assert 'Consultation Requests: 1' in message.body
        assert reverse('adminhub-leads') in message.body

    def test_counter_resets_after_notification(self, client, superuser, low_threshold):
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        client.post(reverse('api-contact'), CONTACT_PAYLOAD)
        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)

        counter = LeadNotificationCounter.load()
        assert counter.survey_count == 0
        assert counter.contact_count == 0
        assert counter.consultation_count == 0

    def test_next_batch_does_not_immediately_refire(self, client, superuser, low_threshold):
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        client.post(reverse('api-contact'), CONTACT_PAYLOAD)
        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)
        assert len(mail.outbox) == 1

        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)
        assert len(mail.outbox) == 1

    def test_no_recipients_does_not_crash(self, client, low_threshold):
        # No superuser fixture used here — zero qualifying recipients.
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        client.post(reverse('api-contact'), CONTACT_PAYLOAD)
        res = client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)

        assert res.status_code == 201
        assert len(mail.outbox) == 0
        assert LeadNotificationCounter.load().total == 0

    def test_not_tied_to_resolved_status(self, client, superuser, low_threshold):
        client.post(reverse('api-survey'), SURVEY_PAYLOAD)
        lead = SurveyRequest.objects.get()
        lead.resolved = True
        lead.save()

        assert LeadNotificationCounter.load().total == 1
        assert len(mail.outbox) == 0

    def test_threshold_is_read_from_site_setting_not_hardcoded(self, client, superuser):
        setting = SiteSetting.load()
        setting.lead_notification_threshold = 2
        setting.save()

        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)
        client.post(reverse('api-consultation'), CONSULTATION_PAYLOAD)

        assert len(mail.outbox) == 1
        assert '2 New Leads' in mail.outbox[0].subject


class TestContactMessageAndConsultationModelsUnaffected:
    """ORM-direct creation (bypassing the API views) must never trigger a
    notification — record_lead_created_and_maybe_notify is only ever called
    from perform_create, never from a model-level signal."""

    def test_orm_create_does_not_increment_counter(self, superuser, low_threshold):
        ContactMessage.objects.create(name='X', phone='9876543210', email='x@example.com')
        ConsultationRequest.objects.create(name='Y', phone='9876543211')

        assert LeadNotificationCounter.load().total == 0
        assert len(mail.outbox) == 0
