from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 4 certificate photos previously lived as hardcoded
# <img> tags pointing at static/image/cert-*.jpg with name/description/meta
# copy hardcoded alongside them in templates/certifications.html. This
# migration copies each source file into a real Certification row (image
# field backed by MEDIA_ROOT) so the Admin Hub can add/delete them without
# touching template code.
CERTIFICATIONS = [
    (
        'cert-iso-9001.jpg',
        'ISO 9001:2015',
        'Quality Management Systems',
        'Valid till 15 Jul 2029',
    ),
    (
        'cert-iso-45001.jpg',
        'ISO 45001:2018',
        'Occupational Health & Safety Management Systems',
        'Valid till 15 Jul 2029',
    ),
    (
        'cert-gst-registration.jpg',
        'GST Registration',
        'Goods & Services Tax, Government of India',
        'GSTIN 26AVPPB0819A1Z3',
    ),
    (
        'cert-udyam-registration.jpg',
        'Udyam Registration',
        'Ministry of MSME, Government of India',
        'UDYAM-DD-03-0011602',
    ),
]


def seed_certifications(apps, schema_editor):
    Certification = apps.get_model('website', 'Certification')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'image'

    for order, (filename, name, description, meta) in enumerate(CERTIFICATIONS, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = Certification(name=name, description=description, meta=meta, order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_certifications(apps, schema_editor):
    Certification = apps.get_model('website', 'Certification')
    Certification.objects.filter(name__in=[name for _, name, _, _ in CERTIFICATIONS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_certification'),
    ]

    operations = [
        migrations.RunPython(seed_certifications, unseed_certifications),
    ]
