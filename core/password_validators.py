import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

SPECIAL_CHARACTERS = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""


class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('This password must contain at least one uppercase letter.'),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _('Your password must contain at least one uppercase letter.')


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not any(char in SPECIAL_CHARACTERS for char in password):
            raise ValidationError(
                _('This password must contain at least one special character (e.g. ! @ # $ %).'),
                code='password_no_special',
            )

    def get_help_text(self):
        return _('Your password must contain at least one special character (e.g. ! @ # $ %).')


class NoWhitespaceValidator:
    def validate(self, password, user=None):
        if re.search(r'\s', password):
            raise ValidationError(
                _('This password must not contain spaces.'),
                code='password_has_whitespace',
            )

    def get_help_text(self):
        return _('Your password must not contain any spaces.')
