import pytest
from django.urls import reverse

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest

pytestmark = pytest.mark.django_db


class TestSurveyRequestCreateView:
    def test_anonymous_can_submit(self, client):
        payload = {
            'name': 'Jane Doe', 'email': 'jane@example.com',
            'address': '123 Long Enough Street Address, City',
            'problem': 'The fire alarm panel keeps beeping intermittently at night.',
            'why_survey': 'We need an on-site assessment before renewing our AMC contract.',
        }
        res = client.post(reverse('api-survey'), payload)
        assert res.status_code == 201
        assert SurveyRequest.objects.count() == 1
        assert SurveyRequest.objects.get().name == 'Jane Doe'

    def test_invalid_payload_rejected_and_nothing_is_created(self, client):
        res = client.post(reverse('api-survey'), {'name': 'J'})
        assert res.status_code == 400
        assert SurveyRequest.objects.count() == 0


class TestContactMessageCreateView:
    def test_anonymous_can_submit(self, client):
        payload = {'name': 'Jane Doe', 'phone': '9876543210', 'email': 'jane@example.com', 'service': 'fire_detection'}
        res = client.post(reverse('api-contact'), payload)
        assert res.status_code == 201
        assert ContactMessage.objects.count() == 1

    def test_invalid_payload_rejected(self, client):
        res = client.post(reverse('api-contact'), {'name': 'Jane Doe', 'phone': '123', 'email': 'jane@example.com'})
        assert res.status_code == 400
        assert ContactMessage.objects.count() == 0


class TestConsultationRequestCreateView:
    def test_anonymous_can_submit(self, client):
        res = client.post(reverse('api-consultation'), {'name': 'Jane Doe', 'phone': '9876543210'})
        assert res.status_code == 201
        assert ConsultationRequest.objects.count() == 1

    def test_invalid_payload_rejected(self, client):
        res = client.post(reverse('api-consultation'), {'name': 'J', 'phone': '9876543210'})
        assert res.status_code == 400
        assert ConsultationRequest.objects.count() == 0
