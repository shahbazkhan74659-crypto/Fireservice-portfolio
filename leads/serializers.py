import re

from rest_framework import serializers

from .models import ContactMessage, SurveyRequest


class SurveyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyRequest
        fields = ['name', 'email', 'address', 'problem', 'why_survey']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        return value

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


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'email', 'service', 'message']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Please enter your full name.')
        return value

    def validate_phone(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) < 7:
            raise serializers.ValidationError('Please enter a valid phone number.')
        return value
