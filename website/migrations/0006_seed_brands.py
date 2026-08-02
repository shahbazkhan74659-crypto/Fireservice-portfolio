from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 5 brand logos previously lived as hardcoded <img> tags
# pointing at static/image/brand-*.png. This migration copies each source
# file into a real Brand row (image field backed by MEDIA_ROOT) so the
# Admin Hub can add/edit/delete them without touching template code.
BRANDS = [
    ('brand-apollo.png', 'Apollo'),
    ('brand-logos-honeywell-group.png', 'System Sensor, Gamewell FCI, Fire-Lite Alarms, Honeywell, Notifier, Silent Knight'),
    ('brand-mitras.png', 'Mitras'),
    ('brand-newage.png', 'NewAge Group of Companies'),
    ('brand-ravel.png', 'Ravel'),
]


def seed_brands(apps, schema_editor):
    Brand = apps.get_model('website', 'Brand')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'SeedImages'

    for order, (filename, name) in enumerate(BRANDS, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = Brand(name=name, order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_brands(apps, schema_editor):
    Brand = apps.get_model('website', 'Brand')
    Brand.objects.filter(name__in=[name for _, name in BRANDS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_brand'),
    ]

    operations = [
        migrations.RunPython(seed_brands, unseed_brands),
    ]
