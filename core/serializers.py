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
