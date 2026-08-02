import re
import xml.etree.ElementTree as ET

from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers

from .models import Brand, Certification, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Product, ProcessPhase, Service, SiteSetting
from .pdf_utils import render_pdf_first_page_to_png

MAX_LOGO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ACCEPTED_ICON_CONTENT_TYPES = {'image/png', 'image/jpeg', 'image/webp', 'image/svg+xml'}
SVG_CONTENT_TYPE = 'image/svg+xml'

# Maps each accepted *raster* content-type to the Pillow-reported format(s) a
# genuine file of that type should decode as. Used so a real JPEG relabeled
# with Content-Type: image/png (or vice versa) is caught too, not just
# outright non-images — Content-Type is entirely client-supplied and must
# never be trusted on its own (see Django's own UploadedFile docs).
RASTER_CONTENT_TYPE_FORMATS = {
    'image/png': {'PNG'},
    'image/jpeg': {'JPEG'},
    'image/webp': {'WEBP'},
}

# Namespace-agnostic: an SVG's <script> or onload= is dangerous regardless of
# which XML namespace prefix (if any) it's declared under, so these checks
# operate on the local (unprefixed) tag/attribute name only.
_DANGEROUS_TAG_LOCALNAMES = {'script'}
_JAVASCRIPT_URI_RE = re.compile(r'^\s*javascript\s*:', re.IGNORECASE)


def _local_name(tag):
    """Strip a `{namespace}localname`-style ElementTree tag/attribute key
    down to just the local name, e.g. `{http://www.w3.org/2000/svg}script`
    -> `script`, `{http://www.w3.org/1999/xlink}href` -> `href`."""
    return tag.rsplit('}', 1)[-1] if '}' in tag else tag


def _svg_bytes_are_safe(raw_bytes):
    """Real content inspection for SVG uploads. Pillow can't validate SVG at
    all (it's XML, not a raster format), so a malicious upload could
    otherwise slip through as long as it declares
    Content-Type: image/svg+xml. Parses the bytes as XML — a real SVG must be
    well-formed XML, so anything that fails to parse is rejected (fail
    closed, not fail open) — then rejects any <script> element, any on*
    event-handler attribute, or a javascript: URI in an href/xlink:href
    attribute."""
    try:
        root = ET.fromstring(raw_bytes)
    except ET.ParseError:
        return False

    for element in root.iter():
        if _local_name(element.tag).lower() in _DANGEROUS_TAG_LOCALNAMES:
            return False
        for attr_name, attr_value in element.attrib.items():
            local_attr = _local_name(attr_name).lower()
            if local_attr.startswith('on'):
                return False
            if local_attr == 'href' and _JAVASCRIPT_URI_RE.match(attr_value or ''):
                return False
    return True


def _raster_bytes_are_valid(file_obj, content_type):
    """Actually decode the uploaded bytes with Pillow rather than trusting
    the claimed Content-Type header. Image.verify() checks the file is a
    genuine, undamaged image of the format Pillow detects; a second, fresh
    open is needed afterward to read img.format, since verify() leaves the
    Image object unusable for further access. Always leaves file_obj's
    position reset to 0 afterward, since Django's storage backend still
    needs to read the full file to actually save it."""
    file_obj.seek(0)
    try:
        with Image.open(file_obj) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        return False
    finally:
        file_obj.seek(0)

    try:
        with Image.open(file_obj) as img:
            detected_format = img.format
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        return False
    finally:
        file_obj.seek(0)

    expected_formats = RASTER_CONTENT_TYPE_FORMATS.get(content_type)
    if expected_formats and detected_format not in expected_formats:
        return False
    return True


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
    uploads, since DRF's ModelSerializer-inferred ImageField validates via
    Pillow, which can't open SVG (a vector/XML format, not a raster one).

    The declared Content-Type header is only used to pick *which* real check
    to run — raster types are decoded and verified with Pillow, SVG is
    parsed as XML and inspected for dangerous content — it is never trusted
    on its own to decide whether the upload is accepted. A file that lies
    about its Content-Type (e.g. real HTML/script served as
    image/svg+xml, or a JPEG relabeled as image/png) is rejected either by
    the wrong-branch check failing or by the format-family cross-check
    inside _raster_bytes_are_valid."""
    if value.size > max_bytes:
        raise serializers.ValidationError(f'Image is too large (max {max_bytes // (1024 * 1024)}MB).')
    content_type = getattr(value, 'content_type', None)
    if content_type not in ACCEPTED_ICON_CONTENT_TYPES:
        raise serializers.ValidationError('Unsupported image type. Use PNG, JPEG, WebP or SVG.')

    if content_type == SVG_CONTENT_TYPE:
        value.seek(0)
        raw_bytes = value.read()
        value.seek(0)
        if not _svg_bytes_are_safe(raw_bytes):
            raise serializers.ValidationError(
                'This SVG file could not be verified as safe (it may contain a script or '
                'event handler, or is not well-formed XML) and was rejected.'
            )
    else:
        if not _raster_bytes_are_valid(value, content_type):
            raise serializers.ValidationError(
                'This file does not appear to be a valid image of the declared type.'
            )

    return value


MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10MB — comfortably covers a scanned multi-page certificate
PDF_CONTENT_TYPE = 'application/pdf'
PDF_MAGIC_BYTES = b'%PDF-'


def validate_pdf_file(value):
    """Same 'never trust Content-Type alone' treatment as
    validate_image_size_and_type() above — a real PDF always starts with the
    '%PDF-' magic bytes, so a mislabeled non-PDF file is rejected here
    instead of only failing later inside PyMuPDF."""
    if value.size > MAX_PDF_SIZE_BYTES:
        raise serializers.ValidationError(f'PDF is too large (max {MAX_PDF_SIZE_BYTES // (1024 * 1024)}MB).')
    if getattr(value, 'content_type', None) != PDF_CONTENT_TYPE:
        raise serializers.ValidationError('Unsupported file type. Upload a PDF.')

    value.seek(0)
    header = value.read(len(PDF_MAGIC_BYTES))
    value.seek(0)
    if header != PDF_MAGIC_BYTES:
        raise serializers.ValidationError('This file is not a valid PDF.')

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
        return validate_image_size_and_type(value)


class CertificationSerializer(serializers.ModelSerializer):
    # Both optional at the serializer level (the model field itself is still
    # required — see create() below, which always fills `image` in one way
    # or another before saving) — validate() requires at least one of the
    # two from the client. Uploading only a PDF renders its first page into
    # `image` automatically, so every template can keep rendering `image`
    # unconditionally regardless of which one the admin actually provided.
    image = serializers.ImageField(required=False)
    pdf = serializers.FileField(required=False)

    class Meta:
        model = Certification
        fields = ['id', 'name', 'description', 'meta', 'image', 'pdf', 'order']
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

    def validate_pdf(self, value):
        return validate_pdf_file(value)

    def validate(self, attrs):
        if not attrs.get('image') and not attrs.get('pdf'):
            raise serializers.ValidationError({'image': 'Upload either a certificate image or a PDF.'})
        return attrs

    def create(self, validated_data):
        pdf_file = validated_data.get('pdf')
        if pdf_file and not validated_data.get('image'):
            base_name = slugify(validated_data.get('name') or 'certificate') or 'certificate'
            try:
                validated_data['image'] = render_pdf_first_page_to_png(pdf_file, base_name)
            except ValueError as exc:
                raise serializers.ValidationError({'pdf': str(exc)})
        return super().create(validated_data)


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


class ProcessPhaseSerializer(serializers.ModelSerializer):
    # Declared explicitly as FileField (not the ModelSerializer-inferred
    # ImageField) so SVG uploads (allowed by the frontend schema) aren't
    # rejected by Pillow — see validate_image_size_and_type() above.
    image = serializers.FileField()

    class Meta:
        model = ProcessPhase
        fields = ['id', 'name', 'image', 'order']
        read_only_fields = ['order']  # server-assigned on create — see perform_create

    def validate_name(self, value):
        return validate_entity_name(value)

    def validate_image(self, value):
        return validate_image_size_and_type(value)
