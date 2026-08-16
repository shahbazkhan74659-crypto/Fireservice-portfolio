import io
import os
import shutil
from pathlib import Path

import pytest
from django.conf import settings as django_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def _link_or_copy(src, dst):
    """copytree's copy_function: hard-link instead of duplicating file bytes
    (media/ is ~5,000 files / 571MB in this project — see _media_root_seed
    below) — falls back to a real copy (copytree's own default behavior) if
    the link can't be created, e.g. a cross-device OSError on a CI
    environment where the destination and the real media/ folder aren't on
    the same volume/drive."""
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


@pytest.fixture(scope='session')
def _media_root_seed(tmp_path_factory, django_db_setup):
    """Session-scoped: does the expensive media/ copy exactly once for the
    whole test run, not once per test function.

    Depends on django_db_setup (otherwise unused) purely to force fixture
    ordering: django_db_setup is what actually applies migrations
    0004/0006/0008/0012/0014, which are what write the seeded image files to
    the real MEDIA_ROOT in the first place — without this dependency,
    session-scoped instantiate-on-first-use gives no guarantee this copy
    runs after those files exist, causing a real FileNotFoundError race.

    Seeded ClientLogo/Product/Certification/ProcessPhase rows (from
    website/migrations/0004,0008,0012,0014 — 0006 also writes files here but
    its seeded Brand rows no longer exist as of 0054_delete_brand) reference
    real image files
    that live under the real project MEDIA_ROOT. `.url` never touches disk
    (string concatenation only), but `.width`/`.height` open the file via
    Pillow and need a real file to exist under whatever MEDIA_ROOT is active
    when a test runs — so seeded rows need this tree available under the
    test MEDIA_ROOT.

    This used to run per-test (function-scoped, copying into each test's own
    tmp_path), which was correct but was ~803,000 total file operations
    across the suite (real project media/ is ~5,000 files / 571MB, times 162
    tests) — the actual cost, independent of copy-vs-hardlink strategy.
    Hoisting the copy to run once per session and having every test just
    point MEDIA_ROOT at this one already-populated directory (see
    _media_root below) is safe because: no test in this suite lists/walks
    MEDIA_ROOT contents directly (no os.listdir/os.walk/glob/raw MEDIA_ROOT
    reference — confirmed by grepping the whole suite) or asserts on its
    file count, and Django's storage backend always writes a test's own
    upload under a fresh, uniquely-suffixed filename
    (FileSystemStorage.get_available_name()), so uploads from different
    tests accumulate in this shared directory across the session without
    colliding with each other or with the seeded files. pytest tears down
    the whole tmp_path_factory session directory at the end of the run
    either way, so there's no cleanup gap.

    Hard-linked (via _link_or_copy) rather than byte-copied since this
    directory and the real media/ folder are on the same drive in this dev
    environment — a directory-entry link is effectively free next to
    copying real file bytes.
    """
    real_media_root = Path(django_settings.MEDIA_ROOT)
    seed_dir = tmp_path_factory.mktemp('media_seed')
    if real_media_root.is_dir():
        shutil.copytree(real_media_root, seed_dir, dirs_exist_ok=True, copy_function=_link_or_copy)
    return seed_dir


@pytest.fixture(autouse=True)
def _media_root(settings, _media_root_seed):
    """Every test points MEDIA_ROOT at the one session-seeded directory
    (built once by _media_root_seed above) instead of getting its own fresh
    copy — see that fixture's docstring for why sharing one directory across
    the whole session is safe here."""
    settings.MEDIA_ROOT = str(_media_root_seed)


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
