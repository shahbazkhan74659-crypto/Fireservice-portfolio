from leads.serializers import (
    ConsultationRequestSerializer,
    ContactMessageSerializer,
    SurveyRequestSerializer,
)

VALID_SURVEY = {
    'name': 'Jane Doe',
    'email': 'jane@example.com',
    'address': '123 Long Enough Street Address, City',
    'problem': 'The fire alarm panel keeps beeping intermittently at night.',
    'why_survey': 'We need an on-site assessment before renewing our AMC contract.',
}


class TestSurveyRequestSerializer:
    def test_valid_payload_is_accepted(self):
        s = SurveyRequestSerializer(data=VALID_SURVEY)
        assert s.is_valid(), s.errors

    def test_short_address_rejected(self):
        s = SurveyRequestSerializer(data={**VALID_SURVEY, 'address': 'Too short'})
        assert not s.is_valid()
        assert 'address' in s.errors

    def test_short_problem_rejected(self):
        s = SurveyRequestSerializer(data={**VALID_SURVEY, 'problem': 'short'})
        assert not s.is_valid()
        assert 'problem' in s.errors

    def test_short_why_survey_rejected(self):
        s = SurveyRequestSerializer(data={**VALID_SURVEY, 'why_survey': 'short'})
        assert not s.is_valid()
        assert 'why_survey' in s.errors

    def test_invalid_email_rejected(self):
        s = SurveyRequestSerializer(data={**VALID_SURVEY, 'email': 'not-an-email'})
        assert not s.is_valid()
        assert 'email' in s.errors

    def test_short_name_rejected(self):
        s = SurveyRequestSerializer(data={**VALID_SURVEY, 'name': 'J'})
        assert not s.is_valid()
        assert 'name' in s.errors


VALID_CONTACT = {
    'name': 'Jane Doe',
    'phone': '9876543210',
    'email': 'jane@example.com',
    'service': 'fire_detection',
    'message': 'Looking for a quote.',
}


class TestContactMessageSerializer:
    def test_valid_payload_is_accepted(self):
        s = ContactMessageSerializer(data=VALID_CONTACT)
        assert s.is_valid(), s.errors

    def test_message_is_optional(self):
        s = ContactMessageSerializer(data={**VALID_CONTACT, 'message': ''})
        assert s.is_valid(), s.errors

    def test_invalid_phone_rejected(self):
        s = ContactMessageSerializer(data={**VALID_CONTACT, 'phone': '123'})
        assert not s.is_valid()
        assert 'phone' in s.errors

    def test_invalid_service_choice_rejected(self):
        s = ContactMessageSerializer(data={**VALID_CONTACT, 'service': 'not_a_real_choice'})
        assert not s.is_valid()
        assert 'service' in s.errors


class TestConsultationRequestSerializer:
    def test_valid_payload_is_accepted(self):
        s = ConsultationRequestSerializer(data={'name': 'Jane Doe', 'phone': '9876543210'})
        assert s.is_valid(), s.errors

    def test_short_name_rejected(self):
        s = ConsultationRequestSerializer(data={'name': 'J', 'phone': '9876543210'})
        assert not s.is_valid()
        assert 'name' in s.errors

    def test_invalid_phone_rejected(self):
        s = ConsultationRequestSerializer(data={'name': 'Jane Doe', 'phone': '123'})
        assert not s.is_valid()
        assert 'phone' in s.errors
