from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# Follow-up to 0008_seed_services.py: replaces each Service row's icon (the
# original inline-SVG-derived icon graphic) with the real photo already used
# for that service's card thumbnail (SERVICE_CARD_IMAGES in
# website_extras.py / admin-services/schema.ts) and hero background
# (services-intro__bg--* in style.css) — now that the Admin Hub's upload
# field for this model accepts only raster images (SVG dropped, see
# RASTER_ONLY_CONTENT_TYPES in serializers.py), the DB-seeded icon should
# match what every other part of the site already displays instead of the
# original vector icon.
#
# Source files are read from static/image/ (not static/SeedImages/) because
# those are the exact files the CSS backgrounds already reference directly
# via url() — duplicating them into SeedImages would just be a second copy
# of the same asset. Reversible back to the original SVGs (still present in
# static/SeedImages/, untouched by this migration).
SERVICE_PHOTOS = {
    'Fire Detection System': (
        'service-fire-detection-system-bg.png', 'service-icon-fire-detection.svg',
    ),
    'Co2 Gas Flooding': (
        'service-co2-gas-flooding-bg.png', 'service-icon-co2-flooding.svg',
    ),
    'CCTV & PA System': (
        'service-cctv-pa-system-bg.png', 'service-icon-cctv-pa.svg',
    ),
    'HVWS / MVWS System': (
        'service-hvws-mvws-system-bg.png', 'service-icon-hvws-mvms.svg',
    ),
    'All Type Fire Extinguisher': (
        'service-fire-extinguishers-bg.png', 'service-icon-fire-extinguisher.svg',
    ),
    'Safety Equipment': (
        'service-safety-equipment-bg.png', 'service-icon-safety-equipment.svg',
    ),
    'Fire Pump House': (
        'service-fire-pump-house-bg.png', 'service-icon-fire-pump-house.svg',
    ),
    'All Type Electricals Work': (
        'service-electrical-works-bg.png', 'service-icon-electricals.svg',
    ),
}


def _apply(apps, filename_index, source_dir_name):
    Service = apps.get_model('website', 'Service')
    source_dir = Path(settings.BASE_DIR) / 'static' / source_dir_name

    for name, filenames in SERVICE_PHOTOS.items():
        filename = filenames[filename_index]
        src = source_dir / filename
        if not src.exists():
            continue
        obj = Service.objects.filter(name=name).first()
        if obj is None:
            continue
        with open(src, 'rb') as f:
            obj.icon.save(filename, File(f), save=True)


def seed_photos(apps, schema_editor):
    _apply(apps, 0, 'image')


def unseed_photos(apps, schema_editor):
    _apply(apps, 1, 'SeedImages')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0037_seed_blog_posts'),
    ]

    operations = [
        migrations.RunPython(seed_photos, unseed_photos),
    ]
