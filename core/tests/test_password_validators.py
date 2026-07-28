import pytest
from django.core.exceptions import ValidationError

from core.password_validators import NoWhitespaceValidator, SpecialCharacterValidator, UppercaseValidator


class TestUppercaseValidator:
    def test_rejects_password_with_no_uppercase(self):
        with pytest.raises(ValidationError):
            UppercaseValidator().validate('all-lowercase-1!')

    def test_accepts_password_with_uppercase(self):
        UppercaseValidator().validate('Has-One-Upper1!')


class TestSpecialCharacterValidator:
    def test_rejects_password_with_no_special_character(self):
        with pytest.raises(ValidationError):
            SpecialCharacterValidator().validate('PlainAlnum123')

    def test_accepts_password_with_special_character(self):
        SpecialCharacterValidator().validate('HasSpecial1!')


class TestNoWhitespaceValidator:
    def test_rejects_password_with_space(self):
        with pytest.raises(ValidationError):
            NoWhitespaceValidator().validate('has a space1!')

    def test_rejects_password_with_tab_or_newline(self):
        with pytest.raises(ValidationError):
            NoWhitespaceValidator().validate('has\ttab1!')
        with pytest.raises(ValidationError):
            NoWhitespaceValidator().validate('has\nnewline1!')

    def test_accepts_password_with_no_whitespace(self):
        NoWhitespaceValidator().validate('NoSpacesHere1!')
