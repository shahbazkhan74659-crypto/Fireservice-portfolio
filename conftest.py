import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    """Every test that touches an ImageField/FileField writes into a fresh
    per-test temp directory instead of the real media/ folder."""
    settings.MEDIA_ROOT = str(tmp_path)


@pytest.fixture
def staff_user(db, django_user_model):
    return django_user_model.objects.create_user(
        'staffuser', 'staff@example.com', 'pw12345!', is_staff=True,
    )


@pytest.fixture
def regular_user(db, django_user_model):
    return django_user_model.objects.create_user(
        'regularuser', 'regular@example.com', 'pw12345!', is_staff=False,
    )


@pytest.fixture
def admin_client(client, staff_user):
    """A Django test Client already logged in as a staff user — named to
    match the project's own `admin_client`/`testadmin` convention used
    throughout manual verification (see CLAUDE.md), not DRF's APIClient."""
    client.force_login(staff_user)
    return client


@pytest.fixture
def make_png_upload():
    """Factory (not a single fixture) since some tests need two distinct
    uploads in one test (e.g. replacing an image) — each call produces a
    genuinely decodable 4x4 PNG, not just bytes labeled as one."""
    def _make(name='test.png'):
        buf = io.BytesIO()
        Image.new('RGB', (4, 4), color='red').save(buf, format='PNG')
        buf.seek(0)
        return SimpleUploadedFile(name, buf.read(), content_type='image/png')
    return _make


@pytest.fixture
def png_upload(make_png_upload):
    return make_png_upload()


@pytest.fixture
def make_svg_upload():
    def _make(svg_bytes, name='test.svg'):
        return SimpleUploadedFile(name, svg_bytes, content_type='image/svg+xml')
    return _make


SAFE_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle r="1"/></svg>'
MALICIOUS_SVG_SCRIPT = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
MALICIOUS_SVG_ONLOAD = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><circle r="1"/></svg>'
MALICIOUS_SVG_JS_HREF = (
    b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
    b'<a xlink:href="javascript:alert(1)"><circle r="1"/></a></svg>'
)


@pytest.fixture
def safe_svg_upload(make_svg_upload):
    return make_svg_upload(SAFE_SVG)


@pytest.fixture
def malicious_svg_script_upload(make_svg_upload):
    return make_svg_upload(MALICIOUS_SVG_SCRIPT, name='evil.svg')


@pytest.fixture
def malicious_svg_onload_upload(make_svg_upload):
    return make_svg_upload(MALICIOUS_SVG_ONLOAD, name='evil.svg')


@pytest.fixture
def malicious_svg_js_href_upload(make_svg_upload):
    return make_svg_upload(MALICIOUS_SVG_JS_HREF, name='evil.svg')


@pytest.fixture
def make_pdf_upload():
    """Factory producing a genuinely openable single-page PDF via PyMuPDF
    itself, not just bytes labeled as one — mirrors make_png_upload's real
    Pillow-decodable image above."""
    def _make(name='test.pdf', pages=1):
        import fitz
        doc = fitz.open()
        for _ in range(pages):
            page = doc.new_page(width=200, height=280)
            page.insert_text((20, 20), 'Test Certificate')
        pdf_bytes = doc.tobytes()
        doc.close()
        return SimpleUploadedFile(name, pdf_bytes, content_type='application/pdf')
    return _make


@pytest.fixture
def pdf_upload(make_pdf_upload):
    return make_pdf_upload()
