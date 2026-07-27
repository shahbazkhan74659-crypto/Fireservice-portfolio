import pytest
from rest_framework import serializers as drf_serializers

from website.serializers import (
    BrandSerializer,
    ClientLogoSerializer,
    validate_entity_name,
    validate_image_size,
    validate_image_size_and_type,
)


class TestValidateEntityName:
    def test_strips_and_accepts_a_valid_name(self):
        assert validate_entity_name('  Acme Corp  ') == 'Acme Corp'

    def test_rejects_too_short(self):
        with pytest.raises(drf_serializers.ValidationError):
            validate_entity_name('A')


class TestValidateImageSize:
    def test_accepts_a_file_under_the_cap(self, png_upload):
        assert validate_image_size(png_upload) is png_upload

    def test_rejects_a_file_over_the_cap(self, png_upload):
        png_upload.size = 6 * 1024 * 1024  # simulate >5MB without generating a huge real file
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size(png_upload)


class TestValidateImageSizeAndType:
    """validate_image_size_and_type() is the real security boundary for every
    Admin Hub image/icon upload (Brand/ClientLogo/Product/Service icons) —
    it never trusts the client-supplied Content-Type on its own, decoding
    raster bytes with Pillow and parsing SVG as XML instead."""

    def test_valid_png_is_accepted(self, png_upload):
        assert validate_image_size_and_type(png_upload) is png_upload

    def test_oversized_file_rejected(self, png_upload):
        png_upload.size = 6 * 1024 * 1024
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(png_upload)

    def test_unsupported_content_type_rejected(self, png_upload):
        png_upload.content_type = 'application/pdf'
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(png_upload)

    def test_mislabeled_content_type_rejected(self, png_upload):
        # Real PNG bytes, but claiming to be a JPEG — the Pillow
        # format cross-check (RASTER_CONTENT_TYPE_FORMATS) should catch it,
        # not just trust the header.
        png_upload.content_type = 'image/jpeg'
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(png_upload)

    def test_safe_svg_is_accepted(self, safe_svg_upload):
        assert validate_image_size_and_type(safe_svg_upload) is safe_svg_upload

    def test_svg_with_script_tag_rejected(self, malicious_svg_script_upload):
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(malicious_svg_script_upload)

    def test_svg_with_onload_handler_rejected(self, malicious_svg_onload_upload):
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(malicious_svg_onload_upload)

    def test_svg_with_javascript_href_rejected(self, malicious_svg_js_href_upload):
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(malicious_svg_js_href_upload)

    def test_malformed_xml_rejected(self, make_svg_upload):
        upload = make_svg_upload(b'<svg><unclosed>', name='broken.svg')
        with pytest.raises(drf_serializers.ValidationError):
            validate_image_size_and_type(upload)


@pytest.mark.django_db
class TestBrandAndClientLogoAcceptSvg:
    """Regression check: CLAUDE.md's history notes flagged Brand/ClientLogo's
    SVG-upload validation as a known-unfixed 'Pillow can't open SVG' bug.
    Reading the current serializers shows both already declare
    `image = serializers.FileField()` explicitly (bypassing DRF's
    Pillow-backed ImageField) and route through validate_image_size_and_type()
    — so this should pass now. If it starts failing, either the fix
    regressed or it was never real; either way, update CLAUDE.md to match."""

    def test_brand_accepts_a_safe_svg_upload(self, safe_svg_upload):
        s = BrandSerializer(data={'name': 'Acme', 'image': safe_svg_upload})
        assert s.is_valid(), s.errors

    def test_client_logo_accepts_a_safe_svg_upload(self, safe_svg_upload):
        s = ClientLogoSerializer(data={'name': 'Acme', 'image': safe_svg_upload})
        assert s.is_valid(), s.errors

    def test_brand_rejects_a_malicious_svg_upload(self, malicious_svg_script_upload):
        s = BrandSerializer(data={'name': 'Acme', 'image': malicious_svg_script_upload})
        assert not s.is_valid()
        assert 'image' in s.errors
