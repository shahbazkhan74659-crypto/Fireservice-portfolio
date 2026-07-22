import re

from rest_framework import serializers

from .models import ConsultationRequest, ContactMessage, SurveyRequest


def validate_person_name(value):
    """Shared name validation used by both SurveyRequestSerializer and
    ContactMessageSerializer — strips whitespace and requires at least 2
    characters."""
    value = value.strip()
    if len(value) < 2:
        raise serializers.ValidationError('Please enter your full name.')
    return value


class SurveyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyRequest
        fields = ['name', 'email', 'address', 'problem', 'why_survey']

    def validate_name(self, value):
        return validate_person_name(value)

    def validate_address(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Please enter a full address.')
        return value

    def validate_problem(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError('Please describe the issue in more detail.')
        return value

    def validate_why_survey(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError('Please tell us why a survey is needed.')
        return value


def validate_phone_number(value):
    """Shared phone validation used by both ContactMessageSerializer and
    ConsultationRequestSerializer — strips non-digits and requires at least
    7 digits."""
    digits = re.sub(r'\D', '', value)
    if len(digits) < 7:
        raise serializers.ValidationError('Please enter a valid phone number.')
    return value.strip()


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'email', 'service', 'message']

    def validate_name(self, value):
        return validate_person_name(value)

    def validate_phone(self, value):
        return validate_phone_number(value)


class ConsultationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        fields = ['name', 'phone']

    def validate_name(self, value):
        return validate_person_name(value)

    def validate_phone(self, value):
        return validate_phone_number(value)
