import pytest
from rest_framework import serializers

from leads.serializers import validate_person_name, validate_phone_number


class TestValidatePersonName:
    def test_strips_and_accepts_valid_name(self):
        assert validate_person_name('  Jane Doe  ') == 'Jane Doe'

    def test_rejects_single_character(self):
        with pytest.raises(serializers.ValidationError):
            validate_person_name('J')

    def test_rejects_whitespace_only(self):
        with pytest.raises(serializers.ValidationError):
            validate_person_name('   ')


class TestValidatePhoneNumber:
    @pytest.mark.parametrize('value', ['9876543210', '+91 98765 43210', '(987) 654-3210'])
    def test_accepts_seven_or_more_digits(self, value):
        assert validate_phone_number(value) == value.strip()

    @pytest.mark.parametrize('value', ['12345', 'abcdef', '123-456'])
    def test_rejects_fewer_than_seven_digits(self, value):
        with pytest.raises(serializers.ValidationError):
            validate_phone_number(value)
