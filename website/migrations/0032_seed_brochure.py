from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: copies the source PDF into the new Brochure row (pdf field
# backed by MEDIA_ROOT) so it's populated on a fresh database. Sourced from
# static/SeedImages/ — brochure.html now reads brochure.pdf.url instead of
# static/files/its-brochure.pdf directly, so that copy was moved into
# SeedImages/ alongside every other DB-seeded content type's source images —
# see CLAUDE.md for why that folder, not static/files/, is where seed
# sources for DB-backed content live.
SOURCE_PDF = 'its-brochure.pdf'


def seed_brochure(apps, schema_editor):
    Brochure = apps.get_model('website', 'Brochure')
    src = Path(settings.BASE_DIR) / 'static' / 'SeedImages' / SOURCE_PDF
    if not src.exists():
        return
    obj, _ = Brochure.objects.get_or_create(pk=1)
    with open(src, 'rb') as f:
        obj.pdf.save(SOURCE_PDF, File(f), save=True)


def unseed_brochure(apps, schema_editor):
    Brochure = apps.get_model('website', 'Brochure')
    Brochure.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0031_brochure'),
    ]

    operations = [
        migrations.RunPython(seed_brochure, unseed_brochure),
    ]
