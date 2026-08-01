import pytest
from rest_framework import serializers as drf_serializers

from website.serializers import (
    BrandSerializer,
    CertificationSerializer,
    ClientLogoSerializer,
    validate_entity_name,
    validate_image_size,
    validate_image_size_and_type,
    validate_pdf_file,
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


class TestValidatePdfFile:
    """validate_pdf_file() is the real security boundary for Certification
    PDF uploads — like validate_image_size_and_type() above, it never trusts
    the client-supplied Content-Type on its own."""

    def test_valid_pdf_is_accepted(self, pdf_upload):
        assert validate_pdf_file(pdf_upload) is pdf_upload

    def test_oversized_file_rejected(self, pdf_upload):
        pdf_upload.size = 11 * 1024 * 1024
        with pytest.raises(drf_serializers.ValidationError):
            validate_pdf_file(pdf_upload)

    def test_unsupported_content_type_rejected(self, pdf_upload):
        pdf_upload.content_type = 'image/png'
        with pytest.raises(drf_serializers.ValidationError):
            validate_pdf_file(pdf_upload)

    def test_mislabeled_content_type_rejected(self, png_upload):
        # Real PNG bytes claiming to be a PDF — the magic-byte check should
        # catch it even though the Content-Type header lies.
        png_upload.content_type = 'application/pdf'
        with pytest.raises(drf_serializers.ValidationError):
            validate_pdf_file(png_upload)


@pytest.mark.django_db
class TestCertificationSerializerPdfUpload:
    """A PDF-uploaded Certification should auto-render its first page into
    `image` server-side, so every template can keep rendering `image`
    unconditionally regardless of which one the admin actually provided."""

    def _valid_payload(self, **overrides):
        payload = {
            'name': 'Udyam Registration',
            'description': 'Ministry of MSME, Government of India',
            'meta': 'UDYAM-DD-03-0011602',
        }
        payload.update(overrides)
        return payload

    def test_pdf_only_upload_is_valid_and_renders_an_image(self, pdf_upload):
        s = CertificationSerializer(data=self._valid_payload(pdf=pdf_upload))
        assert s.is_valid(), s.errors
        certification = s.save(order=1)
        assert certification.pdf.name
        assert certification.image.name
        assert certification.image.name.endswith('.png')

    def test_image_only_upload_still_works_with_no_pdf(self, png_upload):
        s = CertificationSerializer(data=self._valid_payload(image=png_upload))
        assert s.is_valid(), s.errors
        certification = s.save(order=1)
        assert certification.image.name
        assert not certification.pdf

    def test_neither_image_nor_pdf_is_rejected(self):
        s = CertificationSerializer(data=self._valid_payload())
        assert not s.is_valid()
        assert 'image' in s.errors

    def test_non_pdf_file_rejected_under_the_pdf_field(self, png_upload):
        s = CertificationSerializer(data=self._valid_payload(pdf=png_upload))
        assert not s.is_valid()
        assert 'pdf' in s.errors
