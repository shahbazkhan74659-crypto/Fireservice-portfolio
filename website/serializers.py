from rest_framework import serializers

from .models import Brand, Certification, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Product, Service, SiteSetting

MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ACCEPTED_ICON_CONTENT_TYPES = {'image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'}


def validate_entity_name(value):
    """Shared name validation used by every image-backed content model's
    serializer (Brand, ClientLogo, Product, Service, Certification) —
    strips whitespace and requires at least 2 characters."""
    value = value.strip()
    if len(value) < 2:
        raise serializers.ValidationError('Name is required.')
    return value


def validate_image_size(value, max_bytes=MAX_LOGO_SIZE_BYTES):
    """Shared image-size validation used by every image-backed content
    model's serializer — rejects uploads over max_bytes."""
    if value.size > max_bytes:
        raise serializers.ValidationError(f'Image is too large (max {max_bytes // (1024 * 1024)}MB).')
    return value


def validate_image_size_and_type(value, max_bytes=MAX_LOGO_SIZE_BYTES):
    """Shared validation for image-backed fields that must also accept SVG
    uploads — mirrors ServiceSerializer.validate_icon's size + content-type
    checks, since DRF's ModelSerializer-inferred ImageField validates via
    Pillow, which can't open SVG (a vector/XML format, not a raster one)."""
    if value.size > max_bytes:
        raise serializers.ValidationError(f'Image is too large (max {max_bytes // (1024 * 1024)}MB).')
    content_type = getattr(value, 'content_type', None)
    if content_type not in ACCEPTED_ICON_CONTENT_TYPES:
        raise serializers.ValidationError('Unsupported image type. Use PNG, JPEG, WebP or SVG.')
    return value


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
    # Declared explicitly as FileField (not the ModelSerializer-inferred
    # ImageField) so SVG uploads (allowed by the frontend schema) aren't
    # rejected by Pillow — see validate_image_size_and_type() above.
    image = serializers.FileField()

    class Meta:
        model = ClientLogo
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        return validate_entity_name(value)

    def validate_image(self, value):
        return validate_image_size_and_type(value)


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
        return validate_entity_name(value)

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


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'description', 'meta', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        return validate_entity_name(value)

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Description is required.')
        return value

    def validate_meta(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('This field is required.')
        return value

    def validate_image(self, value):
        return validate_image_size(value)


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ['years_experience', 'clients_served', 'installations', 'emergency_support', 'team_members']
        # No max_value set on the model fields, so cap them here.
        extra_kwargs = {
            'years_experience': {'max_value': 999},
            'clients_served': {'max_value': 999999},
            'installations': {'max_value': 999999},
            'emergency_support': {'max_value': 999},
            'team_members': {'max_value': 9999},
        }


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
    # Declared explicitly as FileField (not the ModelSerializer-inferred
    # ImageField) so SVG uploads (allowed by the frontend schema) aren't
    # rejected by Pillow — see validate_image_size_and_type() above.
    image = serializers.FileField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        return validate_entity_name(value)

    def validate_image(self, value):
        return validate_image_size_and_type(value)


class ProductSerializer(serializers.ModelSerializer):
    # Declared explicitly as FileField (not the ModelSerializer-inferred
    # ImageField) so SVG uploads (allowed by the frontend schema) aren't
    # rejected by Pillow — see validate_image_size_and_type() above.
    image = serializers.FileField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        return validate_entity_name(value)

    def validate_image(self, value):
        return validate_image_size_and_type(value)
