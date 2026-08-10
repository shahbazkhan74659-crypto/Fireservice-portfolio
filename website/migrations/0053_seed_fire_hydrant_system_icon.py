from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# Follow-up to 0051_seed_fire_hydrant_system_service.py: that migration left
# icon blank since no photo existed yet for this service. Now that
# service-fire-hydrant-system-bg.png exists in static/image/ (added as the
# page's real hero photo in a later session — see CLAUDE.md), this sets
# Service.icon to the same file, matching every other service row (each
# one's icon is the same photo as its hero background — see
# 0038_seed_service_photos.py). Uses .icon.save() rather than a raw filename
# assignment so the file is actually written through Django's storage
# backend (filesystem in dev, Cloudinary in prod), same as 0038.
SERVICE_NAME = 'Fire Hydrant System'
FILENAME = 'service-fire-hydrant-system-bg.png'


def seed_icon(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    obj = Service.objects.filter(name=SERVICE_NAME).first()
    if obj is None:
        return
    src = Path(settings.BASE_DIR) / 'static' / 'image' / FILENAME
    if not src.exists():
        return
    with open(src, 'rb') as f:
        obj.icon.save(FILENAME, File(f), save=True)


def unseed_icon(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(icon='')


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0052_reorder_services_with_fire_hydrant_and_pava'),
    ]

    operations = [
        migrations.RunPython(seed_icon, unseed_icon),
    ]
