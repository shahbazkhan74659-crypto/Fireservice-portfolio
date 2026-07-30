import re

from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

# Deliberately more permissive than Django's own UnicodeUsernameValidator
# (^[\w.@+-]+$) — spaces are allowed here on purpose (e.g. "Shahbaz Khan"),
# so this can't just reuse the model field's own validators the way the rest
# of this pattern normally would.
USERNAME_ALLOWED_PATTERN = re.compile(r'^[\w.@+ -]+$', re.UNICODE)


class ChangeUsernameSerializer(serializers.Serializer):
    new_username = serializers.CharField()

    def validate_new_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Username is required.')

        User = get_user_model()
        max_length = User._meta.get_field(User.USERNAME_FIELD).max_length
        if max_length and len(value) > max_length:
            raise serializers.ValidationError(f'Too long (max {max_length} characters).')

        if not USERNAME_ALLOWED_PATTERN.match(value):
            raise serializers.ValidationError(
                'Enter a valid username. This value may contain only letters, numbers, spaces, and @/./+/-/_ characters.'
            )

        current_user = self.context['request'].user
        if User.objects.exclude(pk=current_user.pk).filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def save(self):
        user = self.context['request'].user
        user.username = self.validated_data['new_username']
        user.save(update_fields=['username'])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, user=self.context['request'].user)
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class ChangeEmailRequestSerializer(serializers.Serializer):
    """Step 1 of Account Settings' "Change Email" flow — validates the new
    address's format and uniqueness before an OTP is ever sent to it. Doesn't
    write anything itself; the address is only saved once the OTP is
    verified (see AdminHubChangeEmailVerifyOTPView)."""
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        current_user = self.context['request'].user
        if value.lower() == (current_user.email or '').lower():
            raise serializers.ValidationError('This is already your registered email.')

        User = get_user_model()
        if User.objects.exclude(pk=current_user.pk).filter(is_staff=True, email__iexact=value).exists():
            raise serializers.ValidationError('That email is already registered to another admin account.')
        return value


class ChangeEmailVerifyOTPSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    otp = serializers.RegexField(r'^\d{6}$', error_messages={'invalid': 'Enter the 6-digit code.'})


class ForgotPasswordEmailSerializer(serializers.Serializer):
    """Used by both the "send code" and "resend code" requests — just format
    validation. Whether the email actually matches a real staff account is
    checked separately by the view, not here, since that check needs a DB
    lookup the view already has to do anyway to send the email."""
    email = serializers.EmailField()


class ForgotPasswordVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(r'^\d{6}$', error_messages={'invalid': 'Enter the 6-digit code.'})


class ForgotPasswordResetSerializer(serializers.Serializer):
    """No confirm_password field — that mismatch check is UX-only and already
    happens client-side (same "Zod is UX only" convention as every other
    form), and no reset_token field either — the view resolves+consumes the
    token itself before this serializer ever runs, since a spent/expired
    token is a different failure mode (410-style) than an invalid password
    (400-style) and the two shouldn't be reported through the same field."""
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, user=self.context.get('user'))
        return value
