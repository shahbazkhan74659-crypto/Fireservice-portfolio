from rest_framework import serializers

from .models import Brand, ClientLogo, MissionVisionItem

MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class MissionVisionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionVisionItem
        fields = ['id', 'title', 'body', 'points', 'order']

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Title is required.')
        return value

    def validate_body(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters.')
        return value

    def validate_points(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Add at least one checklist point.')
        points = [str(p).strip() for p in value]
        if not all(points):
            raise serializers.ValidationError('Checklist points cannot be empty.')
        return points


class ClientLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientLogo
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Name is required.')
        return value

    def validate_image(self, value):
        if value.size > MAX_LOGO_SIZE_BYTES:
            raise serializers.ValidationError('Image is too large (max 5MB).')
        return value


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Name is required.')
        return value

    def validate_image(self, value):
        if value.size > MAX_LOGO_SIZE_BYTES:
            raise serializers.ValidationError('Image is too large (max 5MB).')
        return value
