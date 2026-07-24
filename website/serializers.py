from rest_framework import serializers

from .models import Brand, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Service

MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ACCEPTED_ICON_CONTENT_TYPES = {'image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'}


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


class ServiceSerializer(serializers.ModelSerializer):
    # Declared explicitly as FileField (not the ModelSerializer-inferred
    # ImageField) because DRF's ImageField validates uploads by opening them
    # with Pillow, which can't open SVG (a vector/XML format, not a raster
    # one) — it would reject every SVG icon even though these are exactly
    # the kind of icon used site-wide. validate_icon() below does the actual
    # type/size checking instead.
    icon = serializers.FileField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'icon', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Name is required.')
        return value

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters.')
        return value

    def validate_icon(self, value):
        if value.size > MAX_LOGO_SIZE_BYTES:
            raise serializers.ValidationError('Image is too large (max 5MB).')
        content_type = getattr(value, 'content_type', None)
        if content_type not in ACCEPTED_ICON_CONTENT_TYPES:
            raise serializers.ValidationError('Unsupported image type. Use PNG, JPEG, WebP or SVG.')
        return value


class FireRiskAssessmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FireRiskAssessmentItem
        fields = ['id', 'text', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_text(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Text is required.')
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
